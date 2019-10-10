import json

import board
import digitalio
import busio
import time
import sys 

import musicplayer
from analogio import AnalogIn
import random

vol_pin = AnalogIn(board.A0)
control_pin = AnalogIn(board.A1)
led_pin = digitalio.DigitalInOut(board.D13)
uart = busio.UART(board.TX, board.RX, baudrate=115200)
busy_pin = digitalio.DigitalInOut(board.A5)
player_uart = busio.UART(board.A2, board.A3, baudrate=9600) 

FILENAME = "/recom.json"

random.seed(vol_pin.value)
input_dict = None
try:
    with open(FILENAME,"r") as fp:
        stored= fp.readlines()
    input_dict = json.loads("\n".join(stored))
except Exception as e:
    print("failed loading",e)

mp = musicplayer.MusicPlayer(vol_pin, control_pin, uart, player_uart, busy_pin, led_pin, save_file = FILENAME, input_dict=input_dict, mp_debug=False)
mp.run()