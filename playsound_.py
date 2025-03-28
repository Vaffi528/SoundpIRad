import sounddevice as sd
import soundfile as sf

def playmusic(index, data, fs, volume):
    # setting the device
    sd.default.device = (int(index))

    sd.play(data*volume, fs)

    status = sd.wait()