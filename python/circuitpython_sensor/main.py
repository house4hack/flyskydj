import board
import busio 
import digitalio
import time
import struct
import ibus
import sys

from vario_sensor import VarioSensor


uart = busio.UART(board.TX, board.RX, baudrate=115200, timeout=ibus.PROTOCOL_GAP)

import adafruit_bmp280
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=118)
sensor.sea_level_pressure = 1013.25

 
led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT


class I2CSensor(VarioSensor):
    def __init__(self,sensor):
        super().__init__() 
        self.sensor = sensor
        self.counter = 0
        # warmup
        for i in range(10): 
            self.alt_offset = sensor.altitude

    def update_measurements(self):
        self.counter += 1
        if self.counter >= 1000:
            self.counter = 0

        alt = self.sensor.altitude - self.alt_offset
        self.update(alt)

        measurements = [alt, self.vibb]
        return measurements

class USBSensor(VarioSensor):
    def __init__(self):
        super().__init__()
        self.measurements = [0,0]

    def update_measurements(self):
        try:
            led.value = True
            
            value = sys.stdin.readline()
            led.value = False
            
            if self.debug:
                print(value, end="")
            alt = float(value.strip())
            self.update(alt)

            self.measurements = [alt, self.vibb]
            
        except Exception as e:
            if self.debug:
                print(e)

        led.value = False
        return self.measurements

class ServoCrow():
    def __init__(self, filename, channel):
        self.filename = filename
        self.channel = channel
        self.dac = audioio.AudioOut(board.A0)
        

    def servo_cb(self, data_arr):
        if data_arr[self.channel]> 1500:
            data = open(self.filename, "rb")
            wav = audioio.WaveFile(data)
            self.dac.play(wav)
            while self.dac.playing:
                pass

        

sensor_types = [ibus.IBUSS_ALT, ibus.IBUSS_VIBB]

doUSB = False
doI2C = True
doCROW = False

if doUSB:
    usbsensor = USBSensor()
    ib = ibus.IBUS(uart, sensor_types, usbsensor.update_measurements, do_log = False)
    ib.start_loop()
elif doI2C:
    i2csensor = I2CSensor(sensor)
    ib = ibus.IBUS(uart, sensor_types, i2csensor.update_measurements, do_log = False)
    ib.start_loop()
elif doCROW:
    import audioio
    servo_crow = ServoCrow("crow.wav",4)
    ib = ibus.IBUS(uart, sensor_types, servo_cb=servo_crow.servo_cb, do_log=True)
    ib.start_loop()
    servo_crow.dac.deinit()



