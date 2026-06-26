# ADB File Explorer
# Stream server — serves a single phone file over HTTP with Range support so
# a browser or player can seek without downloading the whole file.
#
# Core adb primitive (verified):
#   adb -s <serial> exec-out "tail -c +<offset+1> '<path>' | head -c <len>"
# returns exactly <len> raw bytes starting at 0-based byte offset.
#
# Standard library only.

import shlex
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CHUNK = 256 * 1024  # 256 KB read/write chunk size

# Registry: (device_id, remote_path) -> url string
# Ensures we reuse an already-running server for the same file.
_servers = {}
_servers_lock = threading.Lock()


def _get_file_size(adb_path: str, device_id: str, remote_path: str) -> int:
    """Return total byte size of the remote file via `stat -c %s`."""
    cmd = [adb_path, "-s", device_id, "shell", "stat", "-c", "%s",
           shlex.quote(remote_path)]
    out = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT).strip()
    return int(out)


def _spawn_range_reader(adb_path: str, device_id: str, remote_path: str,
                        start: int, length: int):
    """Return a Popen whose stdout emits exactly `length` bytes from `start`."""
    qpath = shlex.quote(remote_path)
    inner = f"tail -c +{start + 1} {qpath} | head -c {length}"
    return subprocess.Popen(
        [adb_path, "-s", device_id, "exec-out", inner],
        stdout=subprocess.PIPE
    )


def _spawn_full_reader(adb_path: str, device_id: str, remote_path: str):
    """Return a Popen whose stdout is the entire remote file."""
    qpath = shlex.quote(remote_path)
    return subprocess.Popen(
        [adb_path, "-s", device_id, "exec-out", f"cat {qpath}"],
        stdout=subprocess.PIPE
    )


def _parse_range(range_header: str, size: int):
    """Parse a 'bytes=START-END' Range header.

    Returns (start, end) inclusive offsets, or None if absent/unsatisfiable.
    Supports bytes=START-END, bytes=START-, bytes=-N (suffix).
    """
    if not range_header or not range_header.startswith("bytes="):
        return None
    spec = range_header[len("bytes="):].strip()
    if "," in spec:
        spec = spec.split(",", 1)[0].strip()
    if "-" not in spec:
        return None
    start_s, end_s = spec.split("-", 1)
    start_s, end_s = start_s.strip(), end_s.strip()
    try:
        if start_s == "":
            if not end_s:
                return None
            n = int(end_s)
            if n <= 0:
                return None
            start = max(0, size - n)
            end = size - 1
        else:
            start = int(start_s)
            end = int(end_s) if end_s else size - 1
    except ValueError:
        return None
    if start < 0 or start >= size:
        return None
    if end >= size:
        end = size - 1
    if end < start:
        return None
    return start, end


def _make_handler_class(adb_path: str, device_id: str, remote_path: str, size: int):
    """Return a request-handler class bound to the given stream parameters."""

    class _Handler(BaseHTTPRequestHandler):
        _adb = adb_path
        _device_id = device_id
        _remote_path = remote_path
        _size = size

        def log_message(self, fmt, *args):  # silence per-request logs
            pass

        def _send_common_headers(self, content_length: int):
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(content_length))

        @staticmethod
        def _kill(proc):
            try:
                if proc.stdout:
                    proc.stdout.close()
            except Exception:
                pass
            if proc.poll() is None:
                try:
                    proc.kill()
                except Exception:
                    pass
            try:
                proc.wait(timeout=5)
            except Exception:
                pass

        def _stream(self, proc):
            import shutil
            try:
                shutil.copyfileobj(proc.stdout, self.wfile, CHUNK)
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                self._kill(proc)

        def _handle(self, send_body: bool):
            if self.path != "/":
                self.send_error(404, "Not Found")
                return

            size = self._size
            range_header = self.headers.get("Range")
            rng = _parse_range(range_header, size) if range_header else None

            if rng is not None:
                start, end = rng
                length = end - start + 1
                try:
                    self.send_response(206)
                    self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
                    self._send_common_headers(length)
                    self.end_headers()
                except (BrokenPipeError, ConnectionResetError):
                    return
                if not send_body:
                    return
                proc = _spawn_range_reader(self._adb, self._device_id,
                                           self._remote_path, start, length)
                self._stream(proc)
            else:
                if range_header is not None:
                    try:
                        self.send_response(416)
                        self.send_header("Content-Range", f"bytes */{size}")
                        self.end_headers()
                    except (BrokenPipeError, ConnectionResetError):
                        pass
                    return
                try:
                    self.send_response(200)
                    self._send_common_headers(size)
                    self.end_headers()
                except (BrokenPipeError, ConnectionResetError):
                    return
                if not send_body:
                    return
                proc = _spawn_full_reader(self._adb, self._device_id,
                                          self._remote_path)
                self._stream(proc)

        def do_GET(self):
            self._handle(send_body=True)

        def do_HEAD(self):
            self._handle(send_body=False)

    return _Handler


def start_stream(adb_path: str, device_id: str, remote_path: str) -> str:
    """Start (or reuse) a localhost HTTP server streaming `remote_path`.

    Returns the URL, e.g. 'http://127.0.0.1:PORT/'.
    One server per (device_id, remote_path) pair; subsequent calls for the
    same pair return the existing URL immediately.
    """
    key = (device_id, remote_path)
    with _servers_lock:
        if key in _servers:
            return _servers[key]

        size = _get_file_size(adb_path, device_id, remote_path)
        handler_cls = _make_handler_class(adb_path, device_id, remote_path, size)

        # Bind to port 0 — the OS picks a free port.
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler_cls)
        port = server.server_address[1]
        url = f"http://127.0.0.1:{port}/"

        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()

        _servers[key] = url
        return url
