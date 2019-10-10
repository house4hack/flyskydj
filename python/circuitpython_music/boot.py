import board
from analogio import AnalogIn
import storage

control_pin = AnalogIn(board.A1)
allow_coding = True
if control_pin.value < 15000:
    allow_coding = False
 
print(allow_coding) 

 
# If the control_pin is set to STOP (i.e. to the top)
# CircuitPython can write to the drive
storage.remount("/", allow_coding )