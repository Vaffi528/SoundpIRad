import sounddevice as sd
import soundfile as sf

# receiveng the info about audiofile and device index
data = input().split('|')
index=data[1]

# extracting data and sampling frequency from the file
data, fs = sf.read(data[0], dtype='float64')

# setting the device
sd.default.device = (int(index))

sd.play(data, fs)

status = sd.wait()