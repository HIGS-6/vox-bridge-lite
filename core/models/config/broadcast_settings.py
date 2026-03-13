from dataclasses import dataclass, field


@dataclass
class BroadcastSettings:
    host: str = "0.0.0.0"
    port: int = 8765
    webclient_port: int = 5735
    sample_rate: int = 44100
    channels: int = 1
    dtype: str = "int16"
    chunk_frames: int = 512
    chunks: int = 512
    connected_clients: set = field(default_factory=set)
