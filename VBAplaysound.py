import sounddevice as sd
import soundfile as sf
import subprocess

# setting a name of the music file
filename = input()

# extracting data and sampling frequency from the file
data, fs = sf.read(filename, dtype='float64')  

# receiving all useful data of the sound devices
devices = sd.query_devices(kind='output')
devicesall = list(sd.query_devices())
hostapis = sd.query_hostapis()

# setting the idexes of devices with needed api
for element in hostapis:
    if element['name'] == 'MME': #or Windows DirectSound, or Windows WASAPI, or Windows WDM-KS
        deviceindexes = element['devices']

# finding the index of needed device
index = None
for element in devicesall:
    if element['name'].startswith('CABLE Input') and 'VB-Audio' in element['name'] and element['index'] in deviceindexes:
        index = int(element['index'])

# setting the device
sd.default.device = (index)

sd.play(data, fs)

# calling the file with playbacking the same sound on the main device via parallel execution
result = subprocess.run("./venv/Scripts/python.exe MAINplaysound.py", input=(f'{filename}|{dict(devices)['index']}').encode('utf-8'))

status = sd.wait()

