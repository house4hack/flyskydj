from busio import UART
from microcontroller import Pin
import time

import board
from digitalio import DigitalInOut, Direction, Pull

def sleep_ms(t):
    time.sleep(t/1000)

def ticks_ms():
    return time.monotonic() * 1000

def ticks_diff(t1, t2):
    return t1-t2

Start_Byte = 0x7E
Version_Byte = 0xFF
Command_Length = 0x06
Acknowledge = 0x00
End_Byte = 0xEF

# inherent delays in DFPlayer
CONFIG_LATENCY = 1000
PLAY_LATENCY =   500
VOLUME_LATENCY = 500

def clamp(x, minimum, maximum):
    return max(minimum, min(x, maximum))

def split(num):
    return num >> 8, num & 0xFF

def kill_time(stamp_ms, kill_ms):
    diff_ms = ticks_diff(ticks_ms(), stamp_ms)
    if diff_ms < kill_ms:
        snooze_ms = kill_ms - diff_ms
        sleep_ms(snooze_ms)
        return snooze_ms
    else:
        return 0

class Player():
    def __init__(self, uart, busy_pin=None, config=True, volume=0.5, debug = False):
        self.debug = debug
        self.playtime = None

        self._volume = None

        self.uart = uart
        if busy_pin is not None:
            busy_pin.direction = Direction.INPUT
            busy_pin.pull = Pull.UP
        self.busy_pin = busy_pin
        if config:
            self.config()
        if volume is not None:
            self.volume(volume)

    def command(self, CMD, Par1, Par2):
        self.awaitconfig()
        Checksum = -(Version_Byte + Command_Length + CMD + Acknowledge + Par1 + Par2)
        HighByte, LowByte = split(Checksum)
        CommandLine = bytes([b & 0xFF for b in [
            Start_Byte, Version_Byte, Command_Length, CMD, Acknowledge,
            Par1, Par2, HighByte, LowByte, End_Byte
        ]])
        if self.debug:
            print([hex(c) for c in CommandLine])
        self.uart.write(CommandLine)

    def query(self, CMD, Par1, Par2):
        response = None
        while response is None:
            self.command(CMD, Par1, Par2)
            response = self.uart.read(10)
        
        if self.debug:
            print('R', [hex(c) for c in response])
        
        value = (response[5]<<8) + response[6]
        return value


    def config(self):
        self.configtime = ticks_ms()
        #self.reset()
        self.command(0x3F, 0x00, 0x00)

    def play(self, folderNum, trackNum):
        self.awaitconfig()
        self.playtime = ticks_ms()
        self.command(0x0F, folderNum, trackNum)

    def finish(self, folderNum, trackNum):
        self.play(folderNum, trackNum)
        while self.playing():
            sleep_ms(50)

    def playing(self):
        if self.busy_pin is not None:
            self.awaitplay()
            return not self.busy_pin.value 
        else:
            raise AssertionError("No busy pin provided, cannot detect play status")

    def awaitconfig(self):
        if self.configtime is not None:
            kill_time(self.configtime, CONFIG_LATENCY)
        self.configtime = None

    def awaitplay(self):
        if self.playtime is not None: # handle delay between playing and registering
            kill_time(self.playtime, PLAY_LATENCY)
        self.playtime = None

    def awaitvolume(self):
        if self.volumetime is not None: # handle delay between playing and registering
            kill_time(self.volumetime, VOLUME_LATENCY)
        self.volumetime = None

    def repeat(self, repeat=True):
        self.awaitconfig()
        val = 1 if repeat else 0
        self.command(0x11, 0, val)

    def _gain(self, gain=1.0):
        self.awaitconfig()
        gain = float(clamp(gain, 0, 1.0))
        val = int(30.0 * gain)
        self.command(0x10,0 ,val)  

    def volume(self, volume=None):
        self.awaitconfig()
        if volume is None:
            return self._volume
        else:
            self._volume = float(clamp(volume, 0, 1.0))
            val = int(30.0 * self._volume)
            self.command(0x06,0 ,val)
            self.volumetime = ticks_ms()

    def standby(self):
        self.awaitconfig()
        self.command(0x0A, 0x00, 0x00)

    def wake(self):
        self.awaitconfig()
        self.command(0x0B, 0x00, 0x00)

    def reset(self):
        self.awaitconfig()
        self.command(0x0C, 0x00, 0x00)

    def stop(self):
        self.awaitconfig()
        self.command(0x16, 0x00, 0x00)


    def query_folders(self):
        return self.query(0x4F,0,0)

    def query_filesInfolder(self, folder):
        return self.query(0x4E,0,folder)

