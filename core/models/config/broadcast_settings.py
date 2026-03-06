from dataclasses import dataclass


@dataclass
class BroadcastSettings:
    host: str = "0.0.0.0"
    port: int = 8765
    sample_rate: int = 44100
    channels: int = 1
    dtype: str = "int16"
    chunk_frames: int = 512
    chunks: int = 512
