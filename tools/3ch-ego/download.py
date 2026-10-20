#!/usr/bin/env python3
# Tool version: 2026-10-19
"""Download one version of an EMG-1 release from its public HTTPS bucket.

Usage:
    python -B tools/download.py BASE_URL DEST [--version v1.0.1]
        [--include GLOB ...] [--exclude GLOB ...] [--workers N] [--list] [--raw]

BASE_URL is the public base URL of the bucket. It is given in the README at
the bucket root, outside the version prefix. The tool fetches
BASE_URL/<version>/SHA256SUMS, selects keys with the include and exclude
patterns, downloads each selected object to DEST/<key> and checks it against
its SHA256 digest. Interrupted runs resume where they stopped.

Standard library only (Python 3.8 or newer). pyarrow is used only if it is
already installed, to read file sizes from MANIFEST.parquet, and only in a
short-lived child process, so this process never loads it. Without pyarrow,
sizes are shown as unknown. The release is public: the tool never sends,
stores or asks for credentials.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import fnmatch
import hashlib
import http.client
import importlib.util
import io
import ipaddress
import json
import os
import random
import re
import shutil
import socket
import ssl
import subprocess
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

TOOL_VERSION = "2026-10-19"  # keep equal to the "# Tool version:" line at the top
DEFAULT_VERSION = "v1.0.1"
SUMS = "SHA256SUMS"
MANIFEST = "MANIFEST.parquet"
RAW_LISTING = "raw/RAW_OBJECTS.csv"
USER_AGENT = "emg1-download/1.0.1 (Python urllib)"
CHUNK = 1 << 20
HASH_BLOCK = 8 << 20
MAX_ATTEMPTS = 100
MANIFEST_READ_TIMEOUT = 120.0
EXIT_OK, EXIT_FAILED, EXIT_SETUP, EXIT_INTERRUPTED = 0, 1, 2, 130

_SUMS_LINE = re.compile(r"([0-9A-Fa-f]{64}) [ *](.+)")
_CONTENT_RANGE = re.compile(r"bytes\s+(\d+)-(\d+)/(\d+|\*)", re.I)
_UNSAFE_CHARS = set('\\:*?"<>|')
_VERSION_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")


# --------------------------------------------------------------------------
# Errors


class SetupError(Exception):
    """A problem that stops the run before files are downloaded."""


class Permanent(Exception):
    """A failure that retrying will not fix."""


class Missing(Permanent):
    """The server says the object does not exist (HTTP 404 or 410)."""


class Transient(Exception):
    """A failure worth retrying after a delay."""

    def __init__(self, message: str, retry_after: Optional[float] = None, progressed: bool = False):
        super().__init__(message)
        self.retry_after = retry_after
        self.progressed = progressed


class Interrupted(Exception):
    """The user stopped the run."""


# --------------------------------------------------------------------------
# Small helpers


def is_loopback(host: str) -> bool:
    host = (host or "").strip("[]").lower()
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def normalise_base_url(raw: str, version: str) -> Tuple[str, Optional[str]]:
    """Check BASE_URL and return (base, note). Rejects anything credential-like."""
    text = (raw or "").strip()
    parts = urllib.parse.urlsplit(text)
    scheme = parts.scheme.lower()
    if scheme not in ("https", "http"):
        raise SetupError("BASE_URL must start with https://")
    if "@" in parts.netloc:
        raise SetupError(
            "BASE_URL must not contain a user name or password. The release is public and needs no credentials."
        )
    if parts.query or parts.fragment or "?" in text or "#" in text:
        raise SetupError(
            "BASE_URL must not contain a query string or fragment. Signed or token URLs are not needed and are not accepted."
        )
    host = parts.hostname
    if not host:
        raise SetupError("BASE_URL has no host name")
    try:
        parts.port
    except ValueError:
        raise SetupError("BASE_URL has an invalid port") from None
    if scheme == "http" and not is_loopback(host):
        raise SetupError(
            "BASE_URL must use https://. Plain http:// is accepted only for localhost, 127.0.0.1 or ::1 (local mirrors and tests)."
        )
    path = parts.path.rstrip("/")
    note = None
    suffix = "/" + version
    if path.endswith(suffix):
        path = path[: -len(suffix)]
        note = "BASE_URL ended with the version prefix {0}; using {0} from --version instead".format(version)
    return urllib.parse.urlunsplit((scheme, parts.netloc, path, "", "")), note


def check_key(key: str, where: str) -> None:
    """Refuse keys that could escape DEST or are not portable file names."""
    bad = (
        not key
        or key.startswith("/")
        or key.endswith("/")
        or any(ord(c) < 32 or ord(c) == 127 for c in key)
        or any(c in _UNSAFE_CHARS for c in key)
    )
    if not bad:
        bad = any(seg in ("", ".", "..") for seg in key.split("/"))
    if bad:
        raise SetupError("{}: refusing unsafe path {!r}".format(where, key))


def parse_sums(text: str) -> Dict[str, str]:
    """Parse SHA256SUMS text into {key: sha256}."""
    entries: Dict[str, str] = {}
    for lineno, line in enumerate(text.split("\n"), 1):
        line = line.rstrip("\r")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("\\"):
            raise SetupError("SHA256SUMS line {}: escaped file names are not supported".format(lineno))
        match = _SUMS_LINE.fullmatch(line)
        if not match:
            raise SetupError('SHA256SUMS line {} is not in "<sha256>  <path>" form'.format(lineno))
        digest, key = match.group(1).lower(), match.group(2)
        if key.startswith("./"):
            key = key[2:]
        check_key(key, "SHA256SUMS line {}".format(lineno))
        if key in entries and entries[key] != digest:
            raise SetupError("SHA256SUMS lists {} twice with different digests".format(key))
        entries[key] = digest
    entries.pop(SUMS, None)
    if not entries:
        raise SetupError("SHA256SUMS lists no files")
    return entries


def norm_etag(value: Optional[str]) -> str:
    value = (value or "").strip()
    if value[:2] in ("W/", "w/"):
        value = value[2:]
    return value.strip().strip('"').strip().lower()


def human(n: Optional[int]) -> str:
    if n is None:
        return "size unknown"
    for unit, div in (("TB", 1e12), ("GB", 1e9), ("MB", 1e6), ("kB", 1e3)):
        if n >= div:
            return "{:.2f} {}".format(n / div, unit)
    return "{} bytes".format(n)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            block = handle.read(HASH_BLOCK)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def unlink_quiet(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass
    except IsADirectoryError:
        pass


def select_keys(keys: Sequence[str], includes: Sequence[str], excludes: Sequence[str]) -> List[str]:
    chosen = []
    for key in keys:
        if includes and not any(fnmatch.fnmatchcase(key, pat) for pat in includes):
            continue
        if any(fnmatch.fnmatchcase(key, pat) for pat in excludes):
            continue
        chosen.append(key)
    return chosen


def unmatched_patterns(keys: Sequence[str], patterns: Sequence[str]) -> List[str]:
    return [pat for pat in patterns if not any(fnmatch.fnmatchcase(k, pat) for k in keys)]


# MANIFEST.parquet is read by this program in a child Python process, and pyarrow
# is imported only there. Reading it in this process was not safe. With threads
# on, pyarrow's worker threads can release a buffer that wraps a Python object
# after the interpreter has started to shut down. CPython then ends that thread
# with pthread_exit, the unwind meets a C++ noexcept destructor, and the process
# aborts with "terminate called without an active exception" (SIGABRT), in up to
# a third of runs on the system where this was found. The child has two guards:
# it reads with use_threads=False, so the buffer is released on its own thread,
# and it leaves with os._exit, so interpreter shutdown never runs. If the child
# still fails in any way, sizes are shown as unknown and nothing else changes.
_MANIFEST_READER = r"""
import json, os, sys

def finish(result, code):
    sys.stdout.write(json.dumps(result))
    sys.stdout.flush()
    os._exit(code)

try:
    sys.path[:] = json.loads(sys.argv[1])
    import pyarrow as pa
    import pyarrow.parquet as pq
except BaseException as exc:
    finish({"load_error": "{}: {}".format(type(exc).__name__, exc)}, 3)
try:
    data = sys.stdin.buffer.read()
    table = pq.read_table(pa.BufferReader(data), columns=["key", "bytes"], use_threads=False)
    rows = [[k, s] for k, s in zip(table.column("key").to_pylist(), table.column("bytes").to_pylist())
            if k is not None and s is not None]
except BaseException as exc:
    finish({"read_error": "{}: {}".format(type(exc).__name__, exc)}, 4)
finish({"sizes": rows}, 0)
"""


def pyarrow_available() -> bool:
    """True if pyarrow can be found on sys.path. Does not import it."""
    try:
        return importlib.util.find_spec("pyarrow") is not None
    except (ImportError, ValueError):
        return False


def manifest_sizes(source) -> Tuple[Optional[Dict[str, int]], str]:
    """Read {key: bytes} from MANIFEST.parquet if pyarrow is installed.

    source is the verified file content (bytes) or a local path. Returns
    (sizes, "") or (None, reason); the caller then shows sizes as unknown.
    """
    if not pyarrow_available():
        return None, "pyarrow is not installed, so MANIFEST.parquet sizes are not read (pip install pyarrow)"
    if not sys.executable or getattr(sys, "frozen", False):
        return None, "cannot start a Python child process to read MANIFEST.parquet sizes"
    try:
        data = bytes(source) if isinstance(source, (bytes, bytearray)) else Path(source).read_bytes()
    except OSError as exc:
        return None, "could not read MANIFEST.parquet: {}".format(exc)
    # The child gets this process's sys.path, so it finds the same pyarrow.
    search_path = json.dumps([entry for entry in sys.path if isinstance(entry, str)])
    command = [sys.executable, "-I", "-S", "-B", "-c", _MANIFEST_READER, search_path]
    try:
        proc = subprocess.run(command, input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              timeout=MANIFEST_READ_TIMEOUT)
    except subprocess.TimeoutExpired:
        return None, "reading MANIFEST.parquet sizes took longer than {:.0f} s".format(MANIFEST_READ_TIMEOUT)
    except OSError as exc:
        return None, "cannot start a Python child process to read MANIFEST.parquet sizes: {}".format(exc)
    try:
        result = json.loads(proc.stdout.decode("utf-8"))
    except ValueError:
        result = None
    if not isinstance(result, dict):
        result = {}
    if proc.returncode == 0 and isinstance(result.get("sizes"), list):
        try:
            return {str(key): int(size) for key, size in result["sizes"]}, ""
        except (TypeError, ValueError):
            pass
    if result.get("load_error"):
        detail = "pyarrow is installed but could not be loaded, so MANIFEST.parquet sizes are not read: {}".format(
            result["load_error"])
    elif result.get("read_error"):
        detail = "could not read MANIFEST.parquet: {}".format(result["read_error"])
    else:
        lines = proc.stderr.decode("utf-8", "replace").strip().splitlines()
        detail = "the child process that reads MANIFEST.parquet sizes exited with status {}{}".format(
            proc.returncode, " ({})".format(lines[-1].strip()) if lines else "")
    return None, detail


@dataclass
class RawRow:
    key: str
    size: int
    etag: str


def parse_raw_listing(text: str, version: str, sums_keys) -> Tuple[List[RawRow], List[Tuple[str, str]]]:
    """Parse raw/RAW_OBJECTS.csv into rows and per-row problems."""
    reader = csv.DictReader(io.StringIO(text))
    fields = reader.fieldnames or []
    if "release_key" in fields:
        column = "release_key"
    elif "key" in fields:
        column = "key"
    else:
        raise SetupError("{} has no release_key or key column".format(RAW_LISTING))
    if "bytes" not in fields:
        raise SetupError("{} has no bytes column".format(RAW_LISTING))
    prefix = version + "/"
    rows: List[RawRow] = []
    problems: List[Tuple[str, str]] = []
    seen: Dict[str, RawRow] = {}
    for lineno, record in enumerate(reader, 2):
        value = (record.get(column) or "").strip()
        label = "{} row {}".format(RAW_LISTING, lineno)
        if not value:
            problems.append((label, "no key listed"))
            continue
        if column == "release_key":
            if not value.startswith(prefix):
                problems.append((value, "release_key is outside the {} prefix".format(prefix)))
                continue
            rel = value[len(prefix):]
        else:
            rel = value[len(prefix):] if value.startswith(prefix) else value
        check_key(rel, label)
        if not rel.startswith("raw/"):
            problems.append((rel, "raw object keys must start with raw/"))
            continue
        if rel in sums_keys:
            problems.append((rel, "also listed in SHA256SUMS; not treated as a raw object"))
            continue
        try:
            size = int((record.get("bytes") or "").strip())
            if size < 0:
                raise ValueError
        except ValueError:
            problems.append((rel, "bytes is not a non-negative integer"))
            continue
        row = RawRow(rel, size, norm_etag(record.get("etag")))
        if rel in seen:
            if (seen[rel].size, seen[rel].etag) != (row.size, row.etag):
                problems.append((rel, "listed twice with different sizes or etags"))
            continue
        seen[rel] = row
        rows.append(row)
    return rows, problems


# --------------------------------------------------------------------------
# HTTP


class _SafeRedirect(urllib.request.HTTPRedirectHandler):
    """Follow redirects only to https (or http on loopback) and never to userinfo URLs."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parts = urllib.parse.urlsplit(newurl)
        scheme = parts.scheme.lower()
        ok = scheme == "https" or (scheme == "http" and is_loopback(parts.hostname or ""))
        if not ok or "@" in parts.netloc:
            raise urllib.error.HTTPError(newurl, code, "refusing redirect to {}".format(scheme or "relative URL"), headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _retry_after(headers) -> Optional[float]:
    try:
        value = float((headers or {}).get("Retry-After", ""))
    except (TypeError, ValueError):
        return None
    return max(0.0, min(value, 300.0))


def classify(exc: BaseException):
    """Map a network exception to Transient, Permanent or Missing (or None)."""
    if isinstance(exc, (Transient, Permanent, Interrupted)):
        return exc
    if isinstance(exc, urllib.error.HTTPError):
        code = exc.code
        message = "HTTP {} {}".format(code, exc.reason)
        retry_after = _retry_after(exc.headers)
        try:
            exc.close()
        except Exception:
            pass
        if code in (404, 410):
            return Missing(message)
        if code in (408, 425, 429) or 500 <= code <= 599:
            return Transient(message, retry_after)
        return Permanent(message)
    if isinstance(exc, urllib.error.URLError):
        reason = exc.reason
        if isinstance(reason, ssl.SSLCertVerificationError):
            return Permanent("TLS certificate check failed: {}".format(reason))
        return Transient("connection error: {}".format(reason))
    if isinstance(exc, ssl.SSLCertVerificationError):
        return Permanent("TLS certificate check failed: {}".format(exc))
    if isinstance(exc, (http.client.HTTPException, socket.timeout, OSError)):
        return Transient("{}: {}".format(type(exc).__name__, exc))
    return None


class Client:
    def __init__(self, base: str, version: str, timeout: float, retries: int, backoff: float,
                 stop: threading.Event, warn: Callable[[str], None]):
        self.base = base
        self.version = version
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff
        self.stop = stop
        self.warn = warn
        context = ssl.create_default_context()
        self.opener = urllib.request.build_opener(_SafeRedirect(), urllib.request.HTTPSHandler(context=context))

    def url(self, key: str) -> str:
        return "{}/{}/{}".format(self.base, self.version, urllib.parse.quote(key, safe="/"))

    def open(self, url: str, headers: Optional[Dict[str, str]] = None):
        merged = {"User-Agent": USER_AGENT, "Accept-Encoding": "identity"}
        merged.update(headers or {})
        request = urllib.request.Request(url, headers=merged, method="GET")
        return self.opener.open(request, timeout=self.timeout)

    def retry(self, attempt: Callable[[], object], label: str):
        failures = 0
        attempts = 0
        while True:
            if self.stop.is_set():
                raise Interrupted()
            attempts += 1
            try:
                return attempt()
            except Transient as exc:
                failures = 0 if exc.progressed else failures + 1
                if failures > self.retries or attempts >= MAX_ATTEMPTS:
                    raise Permanent("{} (gave up after {} attempts)".format(exc, attempts)) from None
                if exc.retry_after is not None:
                    delay = exc.retry_after
                else:
                    delay = min(60.0, self.backoff * (2 ** max(0, failures - 1))) * random.uniform(0.5, 1.0)
                self.warn("retry {}: {}; waiting {:.1f} s".format(label, exc, delay))
                if self.stop.wait(delay):
                    raise Interrupted() from None

    def fetch_bytes(self, key: str, missing_ok: bool = False) -> Optional[bytes]:
        url = self.url(key)

        def attempt() -> bytes:
            try:
                response = self.open(url)
            except Exception as exc:
                mapped = classify(exc)
                if mapped is None:
                    raise
                raise mapped from None
            with response:
                try:
                    data = response.read()
                except Exception as exc:
                    mapped = classify(exc)
                    if mapped is None:
                        raise
                    raise mapped from None
                length = response.headers.get("Content-Length")
            if length and length.isdigit() and int(length) != len(data):
                raise Transient("short read: {} of {} bytes".format(len(data), length))
            return data

        try:
            return self.retry(attempt, key)
        except Missing:
            if missing_ok:
                return None
            raise


def parse_content_range(value: Optional[str]) -> Optional[Tuple[int, int, Optional[int]]]:
    match = _CONTENT_RANGE.fullmatch((value or "").strip())
    if not match:
        return None
    total = None if match.group(3) == "*" else int(match.group(3))
    return int(match.group(1)), int(match.group(2)), total


def unsatisfied_total(value: Optional[str]) -> Optional[int]:
    match = re.fullmatch(r"bytes\s+\*/(\d+)", (value or "").strip(), re.I)
    return int(match.group(1)) if match else None


# --------------------------------------------------------------------------
# Jobs


@dataclass
class Job:
    key: str
    url: str
    final: Path
    sha256: Optional[str] = None
    size: Optional[int] = None
    etag: str = ""
    kind: str = "file"  # "file": checked by SHA256; "raw": checked by size and ETag

    @property
    def part(self) -> Path:
        return self.final.with_name("." + self.final.name + ".partial")


class Downloader:
    def __init__(self, client: Client, dest: Path, workers: int, quiet: bool):
        self.client = client
        self.dest = dest
        self.workers = workers
        self.quiet = quiet
        self.lock = threading.Lock()
        self.counts = {"downloaded": 0, "skipped": 0, "failed": 0}
        self.failures: List[Tuple[str, str]] = []
        self.done = 0
        self.total = 0

    # Output -----------------------------------------------------------
    def info(self, message: str) -> None:
        if not self.quiet:
            with self.lock:
                print(message, flush=True)

    def warn(self, message: str) -> None:
        with self.lock:
            print(message, file=sys.stderr, flush=True)

    def record(self, job: Job, status: str, detail: str) -> None:
        with self.lock:
            self.done += 1
            prefix = "[{}/{}]".format(self.done, self.total)
            if status == "failed":
                self.counts["failed"] += 1
                self.failures.append((job.key, detail))
                print("{} FAILED {}: {}".format(prefix, job.key, detail), file=sys.stderr, flush=True)
            else:
                self.counts[status] += 1
                if not self.quiet:
                    print("{} {} {}{}".format(prefix, status, job.key, " ({})".format(detail) if detail else ""), flush=True)

    # Verification -----------------------------------------------------
    def check_file(self, job: Job, path: Path) -> Tuple[bool, str]:
        size = path.stat().st_size
        if job.size is not None and size != job.size:
            return False, "size is {} bytes, expected {}".format(size, job.size)
        if job.kind == "raw":
            return True, ""
        actual = sha256_file(path)
        if actual != job.sha256:
            return False, "SHA256 mismatch: got {}, SHA256SUMS lists {}".format(actual, job.sha256)
        return True, ""

    # Transfer ---------------------------------------------------------
    def attempt(self, job: Job, state: Dict[str, object]) -> None:
        part = job.part
        offset = part.stat().st_size if part.exists() else 0
        headers: Dict[str, str] = {}
        if offset:
            headers["Range"] = "bytes={}-".format(offset)
            if_range = '"{}"'.format(job.etag) if job.etag else state.get("etag")
            if if_range:
                headers["If-Range"] = str(if_range)
        try:
            response = self.client.open(job.url, headers)
        except urllib.error.HTTPError as exc:
            if exc.code == 416 and offset:
                total = unsatisfied_total(exc.headers.get("Content-Range") if exc.headers else None)
                classify(exc)
                if total is not None and total == offset:
                    # The partial file already holds every byte. It counts as resumed, so if it
                    # does not verify, run_job downloads it once more from the start.
                    state["resumed"] = True
                    return
                unlink_quiet(part)
                raise Transient("partial file did not fit the object; starting again", progressed=True) from None
            raise classify(exc) from None
        except Exception as exc:
            mapped = classify(exc)
            if mapped is None:
                raise
            raise mapped from None

        with response:
            status = response.status
            etag_header = response.headers.get("ETag")
            if job.etag and etag_header and norm_etag(etag_header) != job.etag:
                unlink_quiet(part)
                raise Permanent("server ETag {} differs from the listed etag {}".format(norm_etag(etag_header), job.etag))
            if etag_header and not etag_header.strip().startswith(("W/", "w/")):
                state["etag"] = etag_header.strip()
            if status == 206:
                content_range = parse_content_range(response.headers.get("Content-Range"))
                if content_range is None or content_range[0] != offset:
                    unlink_quiet(part)
                    raise Transient("server returned an unexpected byte range; starting again", progressed=True)
                total = content_range[2]
                mode = "ab"
                state["resumed"] = True
            elif status == 200:
                length = response.headers.get("Content-Length")
                total = int(length) if length and length.isdigit() else None
                mode = "wb"
                state["resumed"] = False
            else:
                raise Permanent("unexpected HTTP status {}".format(status))
            if job.size is not None and total is not None and total != job.size:
                unlink_quiet(part)
                raise Permanent("server reports {} bytes, the listing says {}".format(total, job.size))
            try:
                handle = open(part, mode)
            except OSError as exc:
                raise Permanent("cannot write {}: {}".format(part, exc)) from None
            written = 0
            with handle:
                while True:
                    if self.client.stop.is_set():
                        raise Interrupted()
                    try:
                        chunk = response.read(CHUNK)
                    except Exception as exc:
                        mapped = classify(exc)
                        if mapped is None:
                            raise
                        if isinstance(mapped, Transient):
                            mapped.progressed = written > 0
                        raise mapped from None
                    if not chunk:
                        break
                    try:
                        handle.write(chunk)
                    except OSError as exc:
                        raise Permanent("local write failed: {}".format(exc)) from None
                    written += len(chunk)
        size = part.stat().st_size
        if total is not None and size < total:
            raise Transient("connection ended after {} of {} bytes".format(size, total), progressed=written > 0)
        if total is not None and size > total:
            unlink_quiet(part)
            raise Transient("partial file was longer than the object; starting again", progressed=True)

    def run_job(self, job: Job) -> Tuple[str, str]:
        final = job.final
        if final.is_file():
            ok, why = self.check_file(job, final)
            if ok:
                unlink_quiet(job.part)
                return "skipped", "already present and verified"
            self.warn("{}: existing file does not match ({}); downloading it again".format(job.key, why))
        elif final.exists():
            return "failed", "{} exists and is not a file".format(final)
        try:
            final.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            return "failed", "cannot create {}: {}".format(final.parent, exc)
        state: Dict[str, object] = {}
        restarted = False
        while True:
            self.client.retry(lambda: self.attempt(job, state), job.key)
            ok, why = self.check_file(job, job.part)
            if ok:
                os.replace(str(job.part), str(final))
                return "downloaded", human(final.stat().st_size)
            unlink_quiet(job.part)
            if state.get("resumed") and not restarted:
                restarted = True
                state.clear()
                self.warn("{}: resumed file did not verify ({}); downloading it again from the start".format(job.key, why))
                continue
            return "failed", why

    def safe_run(self, job: Job) -> Tuple[str, str]:
        try:
            return self.run_job(job)
        except Interrupted:
            return "interrupted", ""
        except Permanent as exc:
            return "failed", str(exc)
        except Exception as exc:  # report, never crash the whole run
            return "failed", "unexpected error: {!r}".format(exc)

    def run(self, jobs: Sequence[Job]) -> Dict[str, str]:
        """Run jobs in parallel. Callers add len(jobs) to self.total first."""
        results: Dict[str, str] = {}
        if not jobs:
            return results
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.workers)
        futures = {executor.submit(self.safe_run, job): job for job in jobs}
        try:
            for future in concurrent.futures.as_completed(futures):
                job = futures[future]
                status, detail = future.result()
                if status == "interrupted":
                    continue
                self.record(job, status, detail)
                results[job.key] = status
        except KeyboardInterrupt:
            self.client.stop.set()
            for future in futures:
                future.cancel()
            executor.shutdown(wait=True)
            raise
        executor.shutdown(wait=True)
        if self.client.stop.is_set():
            raise KeyboardInterrupt
        return results


# --------------------------------------------------------------------------
# Command line

DESCRIPTION = """\
Download one version of an EMG-1 dataset release from its public HTTPS bucket
and check every file against SHA256SUMS. No account, key or token is needed,
and this tool never sends credentials.

Tool version: {}""".format(TOOL_VERSION)

EPILOG = """\
BASE_URL is the public base URL of the bucket, as given in the README at the bucket
root (outside the version prefix). Give it without the version; use --version.
DEST is the local folder that becomes the release root, for example emg1-8ch-v1.0.1.

Examples:
  python -B tools/download.py BASE_URL emg1-8ch-v1.0.1 --list
  python -B tools/download.py BASE_URL emg1-8ch-v1.0.1 --exclude 'takes/*' 'derived/*'
  python -B tools/download.py BASE_URL emg1-8ch-v1.0.1 --include 'takes/*/take.h5' 'derived/*'
  python -B tools/download.py BASE_URL emg1-8ch-v1.0.1 --exclude '*.mcap'
  python -B tools/download.py BASE_URL emg1-3ch-v1.0.1 --raw --include 'raw/*/*/CLIP_ID.mcap'

Selection: keys are paths inside the version prefix, such as takes/TAKE/take.h5.
A key is selected when it matches at least one --include pattern (or no --include
is given) and matches no --exclude pattern. Patterns are shell-style wildcards
(Python fnmatch, case-sensitive) and * also matches /. Quote patterns so the shell
does not expand them, and put BASE_URL and DEST before the options. SHA256SUMS and
MANIFEST.parquet are always downloaded.

Sizes: file sizes in --list and in the download plan come from MANIFEST.parquet
and need pyarrow (pip install pyarrow). Without it, --list shows sizes as ? and
the plan gives no total, but downloads still work and every file is still
checked against SHA256SUMS.

Resuming: each file is written to a hidden .NAME.partial file next to its
destination and renamed into place only after it passes its check. Run the same
command again after an interruption: partial files resume with HTTP range
requests, and files that are already present and verified are skipped. Each run
hashes the files that are already present again.

Raw objects (--raw, 3-channel release only) are listed in raw/RAW_OBJECTS.csv, not
in SHA256SUMS. They are checked by byte size and, when the server returns an ETag,
by matching it to the listed etag. raw/README.md describes a content check for a
single recording.

Check the SHA256SUMS digest printed at the start against the digest in the README
at the bucket root, or pass it with --sums-sha256 to have the tool check it.

Summary line: "downloaded" counts files transferred in this run, "skipped" counts
files already present and verified, "verified" counts every selected file that
passed its check (downloaded plus skipped), and "failed" counts files that could
not be downloaded or did not match. Exit status is 0 when nothing failed, 1 when
any file failed, 2 for a setup problem such as a bad BASE_URL or an unreadable
SHA256SUMS, and 130 when interrupted.
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="download.py",
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("base_url", metavar="BASE_URL", help="public base URL of the bucket, without the version prefix")
    parser.add_argument("dest", metavar="DEST", type=Path, help="local release folder (not written with --list)")
    parser.add_argument("--version", dest="release_version", default=DEFAULT_VERSION, metavar="VERSION",
                        help="release version prefix to download (default: {})".format(DEFAULT_VERSION))
    parser.add_argument("--include", action="extend", nargs="+", default=[], metavar="GLOB",
                        help="download only keys matching one of these patterns (may be repeated)")
    parser.add_argument("--exclude", action="extend", nargs="+", default=[], metavar="GLOB",
                        help="skip keys matching any of these patterns (may be repeated)")
    parser.add_argument("--workers", type=int, default=8, metavar="N",
                        help="parallel downloads, 1 to 64 (default: 8)")
    parser.add_argument("--list", action="store_true",
                        help="print the selected keys and total bytes, then stop without downloading")
    parser.add_argument("--raw", action="store_true",
                        help="also fetch the raw MCAP objects listed in raw/RAW_OBJECTS.csv (3-channel release only)")
    parser.add_argument("--sums-sha256", metavar="HEX",
                        help="expected SHA256 of SHA256SUMS, from the README at the bucket root; stop if it differs")
    parser.add_argument("--retries", type=int, default=5, metavar="N",
                        help="retries per file after a network error (default: 5)")
    parser.add_argument("--timeout", type=float, default=60.0, metavar="SECONDS",
                        help="network timeout per read (default: 60)")
    parser.add_argument("--backoff", type=float, default=1.0, metavar="SECONDS",
                        help="first retry delay; later delays double up to 60 s (default: 1)")
    parser.add_argument("--quiet", action="store_true",
                        help="print only the SHA256SUMS digest, problems and the summary")
    return parser


def write_atomic(path: Path, data: bytes) -> None:
    temp = path.with_name("." + path.name + ".partial")
    with open(temp, "wb") as handle:
        handle.write(data)
    os.replace(str(temp), str(path))


def list_mode(args, client: Client, sums: Dict[str, str], sums_bytes: bytes) -> int:
    out = sys.stdout
    keys = sorted(sums)
    sizes: Optional[Dict[str, int]] = None
    fetched: Dict[str, int] = {}
    note = ""
    if MANIFEST in sums:
        data = client.fetch_bytes(MANIFEST)
        if hashlib.sha256(data).hexdigest() != sums[MANIFEST]:
            raise SetupError("MANIFEST.parquet does not match SHA256SUMS")
        fetched[MANIFEST] = len(data)
        sizes, note = manifest_sizes(data)
    else:
        note = "MANIFEST.parquet is not listed in SHA256SUMS, so sizes are unknown"
    selected = select_keys(keys, args.include, args.exclude)
    forced = [k for k in (MANIFEST,) if k in sums and k not in selected]
    raw_rows: List[RawRow] = []
    problems: List[Tuple[str, str]] = []
    raw_missing = False
    if args.raw:
        if RAW_LISTING not in sums:
            raw_missing = True
        else:
            if RAW_LISTING not in selected and RAW_LISTING not in forced:
                forced.append(RAW_LISTING)
            data = client.fetch_bytes(RAW_LISTING)
            if hashlib.sha256(data).hexdigest() != sums[RAW_LISTING]:
                raise SetupError("{} does not match SHA256SUMS".format(RAW_LISTING))
            fetched[RAW_LISTING] = len(data)
            rows, problems = parse_raw_listing(data.decode("utf-8-sig"), args.release_version, sums)
            chosen = set(select_keys([r.key for r in rows], args.include, args.exclude))
            raw_rows = [r for r in rows if r.key in chosen]
            if not rows and not problems:
                print("--raw: {} lists no objects".format(RAW_LISTING), file=sys.stderr)
    known = 0
    unknown = 0
    count = 0
    out.write("{:>15}  {}\n".format(len(sums_bytes), SUMS))
    known += len(sums_bytes)
    count += 1
    for key in sorted(set(selected) | set(forced)):
        size = fetched.get(key)
        if size is None and sizes is not None:
            size = sizes.get(key)
        out.write("{:>15}  {}\n".format(size if size is not None else "?", key))
        count += 1
        if size is None:
            unknown += 1
        else:
            known += size
    for row in raw_rows:
        out.write("{:>15}  {}\n".format(row.size, row.key))
        known += row.size
        count += 1
    if unknown:
        out.write("total: {} files; {} files have unknown size; known sizes add up to {} bytes ({})\n".format(
            count, unknown, known, human(known)))
        if note:
            out.write("note: {}\n".format(note))
    else:
        out.write("total: {} files, {} bytes ({})\n".format(count, known, human(known)))
    if raw_rows or (args.raw and not raw_missing):
        out.write("raw objects: {} selected, {} bytes ({})\n".format(
            len(raw_rows), sum(r.size for r in raw_rows), human(sum(r.size for r in raw_rows))))
    all_keys = keys + ([r.key for r in raw_rows] if args.raw else [])
    for pat in unmatched_patterns(all_keys, args.include):
        print("warning: --include {!r} matched no keys".format(pat), file=sys.stderr)
    status = EXIT_OK
    if raw_missing:
        print("--raw: {} is not listed in SHA256SUMS. Raw objects are part of the 3-channel release only.".format(
            RAW_LISTING), file=sys.stderr)
        status = EXIT_FAILED
    for key, why in problems:
        print("cannot download {}: {}".format(key, why), file=sys.stderr)
        status = EXIT_FAILED
    out.flush()
    return status


def download_mode(args, client: Client, sums: Dict[str, str], sums_bytes: bytes) -> int:
    dest: Path = args.dest
    if dest.exists() and not dest.is_dir():
        raise SetupError("DEST {} exists and is not a folder".format(dest))
    dest.mkdir(parents=True, exist_ok=True)
    sums_path = dest / SUMS
    if sums_path.is_file() and sums_path.read_bytes() != sums_bytes:
        print("note: replacing {} with the server copy".format(sums_path), file=sys.stderr)
    write_atomic(sums_path, sums_bytes)

    runner = Downloader(client, dest, args.workers, args.quiet)
    client.warn = runner.warn
    setup_failed = False

    def make_job(key: str) -> Job:
        return Job(key=key, url=client.url(key), final=dest.joinpath(*key.split("/")), sha256=sums[key])

    keys = sorted(sums)
    selected = select_keys(keys, args.include, args.exclude)
    always = [MANIFEST] if MANIFEST in sums else []
    if args.raw and RAW_LISTING in sums:
        always.append(RAW_LISTING)
    planned = sorted(set(selected) | set(always))
    runner.total = len(planned)

    # MANIFEST.parquet first, so that sizes are known for the plan.
    sizes: Optional[Dict[str, int]] = None
    if MANIFEST in sums:
        runner.run([make_job(MANIFEST)])
        if (dest / MANIFEST).is_file() and runner.failures == []:
            sizes, why = manifest_sizes(dest / MANIFEST)
            if sizes is None:
                runner.info("note: {}".format(why))
    else:
        try:
            data = client.fetch_bytes(MANIFEST, missing_ok=True)
        except Permanent as exc:
            runner.warn("note: MANIFEST.parquet is not listed in SHA256SUMS and could not be fetched: {}".format(exc))
            data = None
        if data is not None:
            write_atomic(dest / MANIFEST, data)
            runner.warn("note: MANIFEST.parquet is not listed in SHA256SUMS; saved without a digest check")

    jobs = []
    for key in planned:
        if key == MANIFEST:
            continue
        job = make_job(key)
        if sizes is not None:
            job.size = sizes.get(key)
        jobs.append(job)
    jobs.sort(key=lambda j: (j.size if j.size is not None else 0, j.key))
    plan = "selected {} of {} files".format(len(planned), len(sums))
    if sizes is not None:
        known = sum(j.size for j in jobs if j.size is not None) + (dest / MANIFEST).stat().st_size
        unknown = sum(1 for j in jobs if j.size is None)
        plan += ", {}".format(human(known))
        if unknown:
            plan += " plus {} files of unknown size".format(unknown)
    runner.info(plan)
    if sizes is not None:
        needed = 0
        for job in jobs:
            if job.size is not None:
                try:
                    present = job.final.stat().st_size == job.size
                except OSError:
                    present = False
                if not present:
                    needed += job.size
        free = shutil.disk_usage(str(dest)).free
        if needed > free:
            runner.warn("warning: about {} still to download but only {} free in {}".format(human(needed), human(free), dest))
    results = runner.run(jobs)

    raw_keys: List[str] = []
    if args.raw:
        if RAW_LISTING not in sums:
            runner.warn("--raw: {} is not listed in SHA256SUMS. Raw objects are part of the 3-channel release only.".format(
                RAW_LISTING))
            setup_failed = True
        elif results.get(RAW_LISTING) not in ("downloaded", "skipped"):
            runner.warn("--raw: {} did not download and verify, so no raw objects were fetched".format(RAW_LISTING))
            setup_failed = True
        else:
            text = (dest / RAW_LISTING).read_text(encoding="utf-8-sig")
            rows, problems = parse_raw_listing(text, args.release_version, sums)
            raw_keys = [r.key for r in rows]
            chosen = set(select_keys(raw_keys, args.include, args.exclude))
            raw_jobs = [
                Job(key=r.key, url=client.url(r.key), final=dest.joinpath(*r.key.split("/")),
                    size=r.size, etag=r.etag, kind="raw")
                for r in rows if r.key in chosen
            ]
            if not rows and not problems:
                runner.warn("--raw: {} lists no objects".format(RAW_LISTING))
            runner.info("raw objects: {} of {} selected, {}".format(
                len(raw_jobs), len(rows), human(sum(j.size or 0 for j in raw_jobs))))
            for key, why in problems:
                runner.total += 1
                runner.record(Job(key=key, url="", final=dest), "failed", why)
            raw_jobs.sort(key=lambda j: (j.size or 0, j.key))
            runner.total += len(raw_jobs)
            runner.run(raw_jobs)
            if raw_jobs:
                runner.info("raw objects were checked by size and ETag; see raw/README.md for a content check")

    for pat in unmatched_patterns(keys + raw_keys, args.include):
        runner.warn("warning: --include {!r} matched no keys".format(pat))
    counts = runner.counts
    if runner.failures:
        print("failed files:", file=sys.stderr)
        for key, why in runner.failures[:50]:
            print("  {}: {}".format(key, why), file=sys.stderr)
        if len(runner.failures) > 50:
            print("  ... and {} more".format(len(runner.failures) - 50), file=sys.stderr)
    print("downloaded {} verified {} skipped {} failed {}".format(
        counts["downloaded"], counts["downloaded"] + counts["skipped"], counts["skipped"], counts["failed"]), flush=True)
    return EXIT_FAILED if counts["failed"] or setup_failed else EXIT_OK


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    stop = threading.Event()

    def warn(message: str) -> None:
        print(message, file=sys.stderr, flush=True)

    try:
        version = args.release_version.strip().strip("/")
        if not _VERSION_RE.fullmatch(version) or ".." in version:
            raise SetupError("--version must look like v1.0.1")
        args.release_version = version
        if not 1 <= args.workers <= 64:
            raise SetupError("--workers must be between 1 and 64")
        if args.retries < 0 or args.timeout <= 0 or args.backoff < 0:
            raise SetupError("--retries, --timeout and --backoff must not be negative")
        for pat in list(args.include) + list(args.exclude):
            if not pat:
                raise SetupError("empty pattern")
        expected_sums = None
        if args.sums_sha256:
            expected_sums = args.sums_sha256.strip().lower()
            if not re.fullmatch(r"[0-9a-f]{64}", expected_sums):
                raise SetupError("--sums-sha256 must be 64 hexadecimal characters")
        base, note = normalise_base_url(args.base_url, version)
        if note:
            warn("note: " + note)
        client = Client(base, version, args.timeout, args.retries, args.backoff, stop, warn)
        try:
            sums_bytes = client.fetch_bytes(SUMS)
        except Missing:
            raise SetupError("no {} at {}; check BASE_URL and --version".format(SUMS, client.url(SUMS))) from None
        except Permanent as exc:
            raise SetupError("could not download {}: {}".format(SUMS, exc)) from None
        sums_digest = hashlib.sha256(sums_bytes).hexdigest()
        if expected_sums and sums_digest != expected_sums:
            raise SetupError("SHA256SUMS digest {} does not match --sums-sha256 {}".format(sums_digest, expected_sums))
        try:
            sums_text = sums_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raise SetupError("SHA256SUMS is not UTF-8 text") from None
        sums = parse_sums(sums_text)
        print("{} for {}: {} files listed, sha256 {}{}".format(
            SUMS, version, len(sums), sums_digest,
            " (matches --sums-sha256)" if expected_sums else " (compare with the README at the bucket root)"),
            file=sys.stderr if args.list else sys.stdout, flush=True)
        if args.list:
            return list_mode(args, client, sums, sums_bytes)
        return download_mode(args, client, sums, sums_bytes)
    except SetupError as exc:
        print("error: {}".format(exc), file=sys.stderr)
        return EXIT_SETUP
    except Permanent as exc:
        print("error: {}".format(exc), file=sys.stderr)
        return EXIT_SETUP
    except (KeyboardInterrupt, Interrupted):
        stop.set()
        print("interrupted; run the same command again to resume", file=sys.stderr)
        return EXIT_INTERRUPTED


if __name__ == "__main__":
    sys.exit(main())
