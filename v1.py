'''import os
import sys
print(f'{os.path.dirname(sys.executable)}, {sys.version}')
########################################################################################################
from pygame._sdl2 import get_audio_device_names
from pygame import mixer
mixer.init()
s = [get_audio_device_names(0)] [['F27G3xTF (NVIDIA High Definition Audio)', 'Динамики (Logitech PRO X Gaming Headset)', 'Realtek Digital Output (Realtek(R) Audio)', 'CABLE Input (VB-Audio Virtual Cable)']]

'''
import pygame as pg
import sys
import asyncio
from aioconsole import ainput

async def main():
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()
        
        keys = pg.key.get_pressed()
        if keys[pg.K_F1]:
            #pg.mixer.pre_init(devicename='Динамики (Logitech PRO X Gaming Headset)')
            pg.mixer.music.set_volume(100)
            pg.mixer.music.load('mcqueenmoments-7240486292394429723_cPiOp3BJ.mp3')
            pg.mixer.music.play()

        input_task = asyncio.create_task(ainput("song: "))
        pg.time.delay(20)
        user_input = await input_task
        pg.mixer.music.set_volume(100)
        pg.mixer.music.load(user_input)
        pg.mixer.music.play()

pg.mixer.init(devicename='CABLE Input (VB-Audio Virtual Cable)')
pg.init()

asyncio.run(main())

