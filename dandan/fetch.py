"""Download the base font and the dictionary data into the local cache.

Every source is listed in SOURCES with the URL it comes from. Pinned sources
(a release tag or a commit) are reproducible; JMdict itself is published daily
by the EDRDG, so the sha256 of what was downloaded is written to
``cache/manifest.json`` for traceability.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tarfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path

CACHE = Path(__file__).resolve().parent.parent / "cache"

JLPT_COMMIT = "b062d4e38c4bdd0950ae1d4ec55f04b176182e03"
FURIGANA_RELEASE = "2.3.1%2B2026-10-25"
GOOGLE_FONTS = "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansjp"


@dataclass(frozen=True)
class Source:
    name: str
    url: str
    filename: str


SOURCES: tuple[Source, ...] = (
    Source("Noto Sans JP (variable)", f"{GOOGLE_FONTS}/NotoSansJP%5Bwght%5D.ttf", "NotoSansJP-VF.ttf"),
    Source("Noto Sans JP OFL", f"{GOOGLE_FONTS}/OFL.txt", "NotoSansJP-OFL.txt"),
    Source("JMdict (English)", "http://ftp.edrdg.org/pub/Nihongo/JMdict_e.gz", "JMdict_e.gz"),
    Source(
        "JmdictFurigana",
        "https://github.com/Doublevil/JmdictFurigana/releases/download/"
        f"{FURIGANA_RELEASE}/JmdictFurigana.json.tar.gz",
        "JmdictFurigana.json.tar.gz",
    ),
    *(
        Source(
            f"JLPT {level.upper()} (yomitan-jlpt-vocab)",
            f"https://raw.githubusercontent.com/stephenmk/yomitan-jlpt-vocab/{JLPT_COMMIT}/original_data/{level}.csv",
            f"jlpt-{level}.csv",
        )
        for level in ("n5", "n4", "n3", "n2", "n1")
    ),
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _download(url: str, target: Path) -> None:
    tmp = target.with_suffix(target.suffix + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": "dandan-font-build"})
    with urllib.request.urlopen(request, timeout=120) as response, tmp.open("wb") as out:
        shutil.copyfileobj(response, out)
    tmp.replace(target)


def _extract_furigana(archive: Path) -> Path:
    target = CACHE / "JmdictFurigana.json"
    if target.exists():
        return target
    with tarfile.open(archive) as tar:
        member = next(m for m in tar.getmembers() if m.name.endswith("JmdictFurigana.json"))
        if not member.isfile():
            raise RuntimeError("unexpected archive member type for JmdictFurigana.json")
        source = tar.extractfile(member)
        if source is None:
            raise RuntimeError("cannot read JmdictFurigana.json from the archive")
        with source, target.open("wb") as out:
            shutil.copyfileobj(source, out)
    return target


def fetch(force: bool = False) -> dict[str, dict[str, str]]:
    """Download every missing source and return the manifest."""
    CACHE.mkdir(exist_ok=True)
    manifest: dict[str, dict[str, str]] = {}
    for source in SOURCES:
        target = CACHE / source.filename
        if force or not target.exists():
            print(f"downloading {source.name} ...", file=sys.stderr)
            _download(source.url, target)
        manifest[source.filename] = {"name": source.name, "url": source.url, "sha256": _sha256(target)}
    _extract_furigana(CACHE / "JmdictFurigana.json.tar.gz")
    (CACHE / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    return manifest


def require(filename: str) -> Path:
    """Return a cached file, fetching the sources first when it is missing."""
    path = CACHE / filename
    if not path.exists():
        fetch()
    return path
