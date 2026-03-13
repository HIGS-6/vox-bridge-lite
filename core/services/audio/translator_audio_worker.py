import logging

import sounddevice as sd

from core.app_state import AppState
from core.models.worker_status import WorkerStatus

log = logging.getLogger("Translator Audio")


class TranslatorAudioWorker:
    def __init__(self, state: AppState):
        self.status = WorkerStatus.STOPPED
        self._state = state
        self._stream = None
        self._on_chunk = None  # set by BroadcastWorker

    def set_chunk_callback(self, fn):
        self._on_chunk = fn

    def start(self):
        if self.status == WorkerStatus.RUNNING:
            print("Translator Audio already running")
            log.warning("Translator Audio already running")
            return

        self.error = None
        try:
            s = self._state.broadcast_settings

            # Check before creating stream
            try:
                sd.check_input_settings(
                    device=self._state.audio_settings.device_idx,
                    channels=s.channels,
                    dtype=s.dtype,
                    samplerate=s.sample_rate,
                )
            except Exception:
                print("Invalid audio settings")
                log.error("Invalid audio settings")
                self.stop()
                return

            self._stream = sd.RawInputStream(
                samplerate=s.sample_rate,
                blocksize=s.chunk_frames,
                device=self._state.audio_settings.device_idx,
                channels=s.channels,
                dtype=s.dtype,
                callback=self._callback,
            )
            self._stream.start()

            self.status = WorkerStatus.RUNNING
            print(
                f"[AudioWorker] Started — device {self._state.audio_settings.device_idx}"
            )
            log.info(f"Started — device {self._state.audio_settings.device_idx}")
        except Exception as e:
            self.error = str(e)
            print(f"Error starting audio worker: {e}")
            log.error(f"Error starting audio worker: {e}")
            self.stop()

    def stop(self):
        if self.status == WorkerStatus.STOPPED:
            print("Translator Audio already stopped")
            log.warning("Translator Audio already stopped")
            return

        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        self.status = WorkerStatus.STOPPED
        print("[AudioWorker] Stopped")
        log.info("Stopped")

    def restart(self):
        self.stop()
        self.start()

    def _callback(self, indata, frames, time, status):
        if status:
            print(f"[AudioWorker] {status}")
            log.warning(f"Callback Status: {status}")

        if self._on_chunk:
            self._on_chunk(bytes(indata))
