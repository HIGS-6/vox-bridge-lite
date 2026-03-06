from core.models.config.broadcast_settings import BroadcastSettings
from core.models.config.preacher_audio_settings import PreacherAudioSettings
from core.models.config.translator_audio_settings import TranslatorAudioSettings


class AppState:
    def __init__(self):
        self.audio_settings = TranslatorAudioSettings()
        self.broadcast_settings = BroadcastSettings()
        self.monitor_settings = PreacherAudioSettings()
