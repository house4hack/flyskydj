import time

class VarioSensor():
    def __init__(self, debug=False):
        self.vario = None
        self.last_measure = None
        self.vibb = None
        self.last_alt = None
        self.debug = debug


    def calc_vario(self, alt):
        alt = float(alt)
        if self.vario is None:
            self.last_measure = time.monotonic()
            self.vario = 0.0
            self.last_alt = alt
            self.vibb = 0.0
        else:
            diff = (alt-self.last_alt)/(time.monotonic() - self.last_measure)
            self.vario = 0.8*self.vario + 0.2*diff
            self.last_alt = alt
            self.last_measure = time.monotonic()

    def calc_vibb(self): 
        if self.vario is None:
            return 0
        else:
            left = 0
            right = 0
            if self.vario > 0.5:
                left = 50 + 5*self.vario
                left = min(200, left)
                left = int(left)
            elif self.vario < -0.5:
                right = 50 - 5*self.vario
                right = min(200, right)
                right = int(right)

            if self.debug:
                print("left",left,"right",right, "vario", self.vario)

            combined = ( left << 8) | right
            combined = int(combined)
            return combined

    def update(self, alt):
        self.calc_vario(alt)
        self.vibb = self.calc_vibb()
        if self.debug:
            print(self.vibb)

