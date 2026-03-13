import asyncio
import json
import logging
import socket
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

import websockets
from websockets.exceptions import ConnectionClosed

from core.app_state import AppState
from core.models.worker_status import WorkerStatus

log = logging.getLogger("Broadcast Worker")

# from core.utils.cert import generate_self_signed_cert


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


class BroadcastWorker:
    def __init__(self, state: AppState):
        self.status = WorkerStatus.STOPPED
        self._state = state
        self._event_loop = None
        self._audio_queue = None
        self._thread = None
        self._http_server_thread = None

    # ── Public API ────────────────────────────────────────────
    def start(self):
        if self.status == WorkerStatus.RUNNING:
            print("Broadcast already running")
            log.info("Broadcast already running")
            return

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

        self.status = WorkerStatus.RUNNING
        print("[BroadcastWorker] Started")
        log.info("Started")

    def stop(self):
        if self.status == WorkerStatus.STOPPED:
            print("Broadcast already stopped")
            log.info("Already stopped")
            return

        if self._event_loop:
            self._event_loop.call_soon_threadsafe(self._event_loop.stop)

        self.status = WorkerStatus.STOPPED
        loop, queue = self._event_loop, self._audio_queue
        self._event_loop = None
        self._audio_queue = None
        if loop and queue:
            loop.call_soon_threadsafe(queue.put_nowait, None)

        print("[BroadcastWorker] Stopped")
        log.info("Stopped")

    def restart(self):
        self.stop()
        if self._thread:
            self._thread.join(timeout=2)

        self.start()

    # ── Called by AudioWorker callback (PortAudio thread) ─────
    def push_chunk(self, chunk: bytes):
        if self._event_loop and self._audio_queue:
            try:
                self._event_loop.call_soon_threadsafe(
                    self._audio_queue.put_nowait, chunk
                )
            except Exception:  # Ingore queue overflow.
                pass
                # print(f"[BroadcastWorker] Error pushing chunk: {e}")

    # ── Internal ──────────────────────────────────────────────
    def _run(self):
        asyncio.run(self._main())

    async def _main(self):
        self._event_loop = asyncio.get_running_loop()
        self._audio_queue = asyncio.Queue(maxsize=100)
        s = self._state.broadcast_settings

        self._start_http_server()

        # import ssl

        # cert_file, key_file = generate_self_signed_cert()
        # ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        # ssl_ctx.load_cert_chain(cert_file, key_file)

        print(f"[BroadcastWorker] ws://{s.host}:{s.port}")
        log.info(f"Websocket hosted at: ws://{s.host}:{s.port}")
        async with websockets.serve(self._handler, s.host, s.port):
            await self._broadcast_loop()

    async def _broadcast_loop(self):
        if self._audio_queue is None:
            raise ValueError("Audio queue is not initialized")

        while not self.status == WorkerStatus.STOPPED:
            chunk = await self._audio_queue.get()
            if not self._state.broadcast_settings.connected_clients:
                continue
            dead = set()
            for ws in list(self._state.broadcast_settings.connected_clients):
                try:
                    await ws.send(chunk)
                except Exception:
                    dead.add(ws)
            self._state.broadcast_settings.connected_clients -= dead

    async def _handler(self, ws):
        addr = ws.remote_address
        print(f"[BroadcastWorker] Client connected: {addr[0]}:{addr[1]}")
        log.info(f"Client connected: {addr[0]}:{addr[1]}")
        self._state.broadcast_settings.connected_clients.add(ws)

        s = self._state.broadcast_settings
        await ws.send(
            json.dumps(
                {
                    "type": "config",
                    "sampleRate": s.sample_rate,
                    "channels": s.channels,
                    "dtype": s.dtype,
                    "chunkFrames": s.chunks,
                }
            )
        )

        try:
            async for _ in ws:
                pass
        except ConnectionClosed:
            pass
        finally:
            self._state.broadcast_settings.connected_clients.discard(ws)
            print(f"[BroadcastWorker] Client disconnected: {addr[0]}:{addr[1]}")
            log.info(f"Client disconnected: {addr[0]}:{addr[1]}")

    def _start_http_server(self):
        # import ssl

        if self._http_server_thread:
            print("HTTP server already running")
            log.info("HTTP server already running")
            return

        from core.utils import resource_path

        directory = resource_path("assets/webclient")

        class DirHandler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory, **kwargs)

        def _serve():
            httpd = ThreadingHTTPServer(
                ("0.0.0.0", self._state.broadcast_settings.webclient_port), DirHandler
            )

            # Wrap con SSL
            # cert_file, key_file = generate_self_signed_cert()
            # ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            # ctx.load_cert_chain(cert_file, key_file)
            # httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)

            print(
                f"[BroadcastWorker] Web client at http://0.0.0.0:{self._state.broadcast_settings.webclient_port}"
            )
            log.info(
                f"Web client at http://0.0.0.0:{self._state.broadcast_settings.webclient_port}"
            )
            httpd.serve_forever()

        self._http_server_thread = threading.Thread(
            target=_serve, daemon=True, name="HTTPServer"
        ).start()
