import sounddevice as sd
import soundfile as sf

def playmusic(index, data, fs):
    # setting the device
    sd.default.device = (int(index))

    sd.play(data, fs)

    status = sd.wait()