from dataclasses import dataclass


@dataclass
class TranslatorAudioSettings:
    device_idx: int = 0
    volume: float = 1.0
