"""Disk cache for ADB EXIF thumbnails."""
import hashlib
import os
import tempfile


def _cache_dir() -> str:
    d = os.path.join(tempfile.gettempdir(), "adbfe_thumbs")
    os.makedirs(d, exist_ok=True)
    return d


def _key(serial: str, path: str, mtime_iso: str) -> str:
    raw = f"{serial}:{path}:{mtime_iso}"
    return hashlib.sha256(raw.encode()).hexdigest() + ".jpg"


def get(serial: str, path: str, mtime_iso: str):
    """Return cached bytes or None."""
    fpath = os.path.join(_cache_dir(), _key(serial, path, mtime_iso))
    if os.path.exists(fpath):
        try:
            with open(fpath, "rb") as f:
                return f.read()
        except Exception:
            return None
    return None


def put(serial: str, path: str, mtime_iso: str, data: bytes) -> None:
    """Store bytes in disk cache."""
    fpath = os.path.join(_cache_dir(), _key(serial, path, mtime_iso))
    try:
        with open(fpath, "wb") as f:
            f.write(data)
    except Exception:
        pass
