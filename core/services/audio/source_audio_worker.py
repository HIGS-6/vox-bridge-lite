import logging

import sounddevice as sd

from core.app_state import AppState
from core.models.worker_status import WorkerStatus
from core.services.audio.utils import config_from_input

log = logging.getLogger("Source Audio")


class SourceAudioWorker:
    """
    Captures preacher's wireless mic (input device) and
    routes it directly to the translator's headphones (output device).
    No processing — just passthrough.
    """

    def __init__(self, state: AppState):
        self.status = WorkerStatus.STOPPED
        self._state = state
        self._stream = None

    # ── Public API ────────────────────────────────────────────
    def start(self):
        self.error = None

        if self.status == WorkerStatus.RUNNING:
            print("Preacher Audio Already Running")
            log.warning("Preacher Audio Already Running")
            return

        try:
            input_device_idx = self._state.monitor_settings.input_device_idx
            output_device_idx = self._state.monitor_settings.output_device_idx

            # s = self._state.broadcast_settings
            config = config_from_input(input_device_idx)
            if config is None:
                print("Invalid Config")
                log.error("Invalid Config")
                return

            sr, channels, h = config

            # Check before creating stream
            try:
                sd.check_input_settings(
                    device=input_device_idx,
                    channels=channels,
                    samplerate=sr,
                    dtype="float32",
                )
            except Exception:
                print("Invalid audio settings")
                log.error("Invalid audio settings")
                self.stop()
                return

            sd.check_input_settings(
                device=input_device_idx,
                channels=channels,
                samplerate=sr,
                dtype="float32",
            )
            self._stream = sd.Stream(
                samplerate=sr,
                blocksize=512,
                device=(input_device_idx, output_device_idx),
                channels=channels,
                dtype="float32",
                callback=self._callback,
            )
            self._stream.start()

            self.status = WorkerStatus.RUNNING
            print(f"[PreacherMonitor] {input_device_idx} → {output_device_idx}")
            log.info(f"{input_device_idx} → {output_device_idx}")
        except Exception as e:
            self.error = str(e)

            print(f"Error starting stream: {e}")
            log.error(f"Error starting stream: {e}")

            self.stop()

    def stop(self):
        if self.status == WorkerStatus.STOPPED:
            print("Preacher Audio Already Stopped")
            log.warning("Preacher Audio Already Stopped")
            return

        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        self.status = WorkerStatus.STOPPED
        print("[PreacherMonitor] Stopped")
        log.info("Stopped")

    def restart(self):
        self.stop()
        self.start()

    # ── Passthrough callback (PortAudio thread) ───────────────
    def _callback(self, indata, outdata, frames, time, status):
        if status:
            print(f"[PreacherMonitor] {status}")
            log.warning(f"{status}")

        outdata[:] = indata * self._state.audio_settings.volume
