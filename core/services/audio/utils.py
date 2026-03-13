import sounddevice as sd


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
        if d["max_input_channels"] <= 0:
            continue
        name = d["name"]
        if "hdmi" in name.lower():
            continue
        try:
            cfg = config_from_input(i)

            if cfg is None:
                continue

            sr, ch, _ = cfg

            sd.check_input_settings(
                device=i,
                channels=ch,
                dtype="int16",
                samplerate=sr,
            )
            inputs.append((i, name))
        except Exception:
            continue
    return inputs


def list_output_devices():
    outputs = []
    for i, d in enumerate(sd.query_devices()):
        if d["max_output_channels"] <= 0:
            continue

        name = d["name"]
        try:
            sd.check_output_settings(
                device=i,
                channels=1,
                dtype="int16",
                samplerate=44100,
            )
            outputs.append((i, name))
        except Exception:
            continue
    return outputs
