# ADB File Explorer
# Stream server — thin wrapper over the SHARED range-stream core.
#
# There used to be a second, independent copy of the whole Range/adb HTTP server
# right here (~200 lines). It drifted from the original: it never got the
# "filename + extension in the stream URL" fix, so QuickTime failed on its links
# with err -11828, and it announced every file as video/mp4. It also leaked one
# HTTP server per copied link — the registry stored the URL but not the server,
# and nothing ever called shutdown().
#
# The core now lives in ONE place: adb_stream.py in the shared scripts dir (the
# same file the tray's phone-stream.sh runs). Fix it there, and the CLI, the tray
# and this app all get the fix. What stays here is only what is specific to this
# app: the per-file registry and closing everything when the window closes.

import importlib.util
import threading

from app.core.configurations import AppScripts

_core = None
_core_lock = threading.Lock()

# (device_id, remote_path) -> (url, server)
_servers = {}
_servers_lock = threading.Lock()


def _load_core():
    """Import adb_stream.py by path — it is a standalone script, not a package."""
    global _core
    with _core_lock:
        if _core is None:
            spec = importlib.util.spec_from_file_location(
                "adb_stream", AppScripts.ADB_STREAM
            )
            if spec is None or spec.loader is None:
                raise RuntimeError("Stream core not found: %s" % AppScripts.ADB_STREAM)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            _core = module
    return _core


def start_stream(adb_path: str, device_id: str, remote_path: str) -> str:
    """Start (or reuse) a localhost HTTP server streaming `remote_path`.

    Returns the URL. One server per (device_id, remote_path); the URL carries the
    real filename so players can tell the container from the extension.
    """
    core = _load_core()
    key = (device_id, remote_path)
    with _servers_lock:
        existing = _servers.get(key)
        if existing:
            return existing[0]
        url, server = core.start_server(
            remote_path, serial=device_id, adb=adb_path, port=0
        )
        _servers[key] = (url, server)
        return url


def stop_all():
    """Close every server started this session. Called when the app quits —
    without this each streamed file leaves a listening socket behind."""
    with _servers_lock:
        for _url, server in _servers.values():
            try:
                server.shutdown()
                server.server_close()
            except Exception:
                pass
        _servers.clear()
