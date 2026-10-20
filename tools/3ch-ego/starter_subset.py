"""One starter selection used by the download commands, verifier and local mirror test.

aws_patterns keeps its historical name: the list is last-match-wins, starting with exclude-all.
tools/download.py takes the same includes and the trailing excludes as --include/--exclude.
"""
from fnmatch import fnmatchcase
PREFIXES=('starter/*','vendor/*','index/*.csv','index/*.parquet','splits/*','eval/*','taxonomy/*','loader/*','tests/*','tools/*','baseline/*','baselines/*','cameras/*','provenance/*')
EXACT=('raw/RAW_OBJECTS.csv','raw/README.md','copy_manifest.csv','LICENSE','LICENSE-CODE','SHA256SUMS','MANIFEST.parquet')
# SHA256SUMS does not list itself, so an --include for it matches no listed key; tools/download.py
# always fetches it (and MANIFEST.parquet). It stays in the starter selection but not in the documented includes.
UNLISTED_ALWAYS_FETCHED=('SHA256SUMS',)
def download_includes(patterns):return [pattern for mode,pattern in patterns[1:] if mode=='include' and pattern not in UNLISTED_ALWAYS_FETCHED]
def root_docs(keys):return tuple(sorted(k for k in keys if '/' not in k and (k.endswith(('.md','.json','.cff')) or k.startswith('requirements') and k.endswith('.txt'))))
def aws_patterns(keys):
 return [('exclude','*')]+[('include',p) for p in PREFIXES]+[('include',p) for p in EXACT+root_docs(keys)]+[('exclude','index/video_frames/*'),('exclude','*.mcap')]
def selected(key,patterns):
 state=False
 for mode,pattern in patterns:
  if fnmatchcase(key,pattern):state=(mode=='include')
 return state
