import vario_sensor
import busio 
import board
import sys
import supervisor
import digitalio
import time
import json
import random
import recommender
import dfplayer


STOP=1
PLAY=2
SKIP=3
TRAIN=4


class MusicPlayer(vario_sensor.VarioSensor):
    def __init__(self, vol_pin, control_pin, uart, player_uart, busy_pin, led_pin=None, save_file=None, input_dict=None, mp_debug=False):
        super().__init__()
        if led_pin is not None:
            self.led = led_pin
            self.led.direction = digitalio.Direction.OUTPUT

            
        self.state = SKIP
        self.classIx = -1

        self.mp_debug = mp_debug
        self.last_start = 0
        self.save_file = save_file

        ### new
        self.player = dfplayer.Player(busy_pin=busy_pin, uart=player_uart)
        self.vol_pin = vol_pin
        self.volume = 0
        self.control_pin = control_pin
        self.uart = uart

        #Load trained model
        self.classCount = self.player.query_folders()
        if input_dict is None:
            self.rec = recommender.Recommender(self.classCount)
        else:
            self.rec = recommender.Recommender(self.classCount)
            self.rec.load(input_dict)



        self.songs = {}
        for folder in range(self.classCount):
            self.songs['ix_group_%d' % folder] = 0
            songCount = self.player.query_filesInfolder(folder+1)
            self.songs['group_%d' % folder] = range(songCount)

        for i in range(self.classCount):
            self.songs['group_%d' % i] = sorted(self.songs['group_%d' % i], key=lambda x: random.random())



    def read_uart(self):
        try:
            data = self.uart.readline().strip()

            if data != b'':
                alt = float(data)/10 - 100
                self.update(alt)
                
                self.rec.update_reading(alt, self.vario)
                if self.mp_debug:
                    pass
                    #print(alt, self.vario, end="\n")
                    
        except:
            pass


    def stop(self):
        self.player.stop()
        while self.player.playing():
            time.sleep(0.1)
        time.sleep(0.5)

    def do_next_song(self):
        self.classIx = self.rec.recommend()

        song_ix = self.songs["ix_group_%d" % self.classIx]
        song_ix += 1
        songs = self.songs["group_%d" % self.classIx]


        if song_ix >= len(songs):
            song_ix = 0

        self.stop()
        self.player.play(self.classIx+1,songs[song_ix]+1)
        #print(self.classIx+1, songs[song_ix]+1)

        self.songs["ix_group_%d" % self.classIx] = song_ix
        self.last_start = time.monotonic()

    def do_save(self):
        saved_dict = self.rec.save()
        try:
            if self.save_file is not None:
                with open(self.save_file, "w") as fp:
                    json.dump(saved_dict, fp)
        except Exception as e:
            if self.mp_debug:
                print("failed to save",e)
        if self.mp_debug:
            print(json.dumps(saved_dict))


    def update_volume(self):
        vol = self.vol_pin.value / 65536
        if abs(vol - self.volume) > 0.05:
            self.volume= vol
            self.player.volume(vol)

    def get_control(self):
        if self.control_pin.value > 56000:
            return PLAY
        elif self.control_pin.value > 28000:
            return SKIP
        else:
            return STOP
        

    def run(self):
        while True:
            try:
                self.read_uart()
                self.update_volume()
                control = self.get_control()
                if control == SKIP:
                    
                    if self.state != SKIP:
                        if self.mp_debug:
                            print("SKIP")
                        self.state = SKIP

                    elif self.state == SKIP:
                        pass # just ignore, pauses playing
                elif control == STOP:
                    if self.state != STOP:
                        self.stop()
                        self.state = STOP
                        self.do_save()
                        if self.mp_debug:
                            print("STOPPED")
                else:
                    if self.state == SKIP or self.state == STOP:
                        self.state = PLAY
                        self.rec.train(self.classIx, 0)
                        self.do_next_song()
                    elif self.state == PLAY:
                        if time.monotonic() - self.last_start > 40:
                            self.state = TRAIN
                            self.rec.train(self.classIx, 1)
                            if self.mp_debug:
                                print(self.classIx, "CONFIRMED")
                    elif self.state == TRAIN:
                        #if time.monotonic() - self.last_start > 30:
                        if not self.player.playing():
                            self.state = PLAY
                            self.do_next_song()
                    elif self.state == STOP:
                        pass

            except Exception as e:
                if self.mp_debug:
                    print("fail",str(e))


