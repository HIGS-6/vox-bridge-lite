import sounddevice as sd

from core.app_state import AppState
from core.models.worker_status import WorkerStatus


def config_from_input(device_index):
    try:
        info = sd.query_devices(device_index, "input")
    except Exception:
        print("No")
        return

    samplerate = int(info["default_samplerate"])

    # casi siempre mono es correcto
    channels = 1 if info["max_input_channels"] >= 1 else 0

    latency = info["default_low_input_latency"]

    return samplerate, channels, latency


def get_preferred_hostapi():
    for i, api in enumerate(sd.query_hostapis()):
        name = api["name"].lower()

        if "pipewire" in name:
            return i
        if "pulse" in name:
            return i

    return None


def list_input_devices():
    inputs = []

    for i, d in enumerate(sd.query_devices()):
        if d["max_input_channels"] > 0:
            name = d["name"]

            # ignorar basura HDMI
            if "hdmi" in name.lower():
                continue

            inputs.append((i, name))

    return inputs


def get_available_devices(**kwargs):
    devices = sd.query_devices(**kwargs)
    return devices


class TranslatorWorker:
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
        except Exception as e:
            self.error = str(e)
            print(f"Error starting audio worker: {e}")
            self.stop()

    def stop(self):
        if self.status == WorkerStatus.STOPPED:
            print("Translator Audio already stopped")
            return

        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        self.status = WorkerStatus.STOPPED
        print("[AudioWorker] Stopped")

    def restart(self):
        self.stop()
        self.start()

    def _callback(self, indata, frames, time, status):
        if status:
            print(f"[AudioWorker] {status}")
        if self._on_chunk:
            self._on_chunk(bytes(indata))


class PreacherMonitorWorker:
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
            print("Already Running")
            return

        try:
            input_device_idx = self._state.monitor_settings.input_device_idx
            output_device_idx = self._state.monitor_settings.output_device_idx

            # s = self._state.broadcast_settings
            config = config_from_input(input_device_idx)
            if config is None:
                print("Invalid Config")
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
        except Exception as e:
            self.error = str(e)
            print(f"Error starting stream: {e}")
            self.stop()

    def stop(self):
        if self.status == WorkerStatus.STOPPED:
            print("Already Stopped")
            return

        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        self.status = WorkerStatus.STOPPED
        print("[PreacherMonitor] Stopped")

    def restart(self):
        self.stop()
        self.start()

    # ── Passthrough callback (PortAudio thread) ───────────────
    def _callback(self, indata, outdata, frames, time, status):
        if status:
            print(f"[PreacherMonitor] {status}")
        outdata[:] = indata
