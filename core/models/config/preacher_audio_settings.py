from dataclasses import dataclass


@dataclass
class PreacherAudioSettings:
    input_device_idx: int = 0
    output_device_idx: int = 1
