# imports
# -------
import time
from picamera2.encoders import H264Encoder
from picamera2 import Picamera2
from smbus import SMBus
import random
# -------

# camera setup
# ------------
camera = Picamera2() # initialize a PiCamera2 object
video_config = camera.create_video_configuration() # set a configuration
camera.configure(video_config) # configure the object

encoder = H264Encoder(bitrate = 1000000) # set the encoder
output = 'test2.h264' # set the file destination
# ------------

# ADC setup
# ---------
ADC_REGISTER = 0x68 # set ADC register value
bus = SMBus(1) # initialize a new I2C bus
bus.write_byte(ADC_REGISTER, 0x10) # Continuous conversion mode, 12 bit resolution
# ---------

# Function to run ADC
# -------------------
def get_voltage():
    data = bus.read_i2c_block_data(ADC_REGISTER, 0x00, 2) # read two bytes back from 0x00
    voltage = (data[0] & 0x0F) * 256 + data[1] # convert value into voltage
    if voltage > 2047:
        voltage -= 4095 # handle overflow
    return voltage
# -------------------
    
# bool FLIGHT = False # Flight status
timer = 60

# start recording / capturing voltage data
# ----------------------------------------
x = 0
camera.start_recording(encoder, output)
with open('voltage_data.csv', "a", newline='') as csv_file:
    while x < timer:
        voltage = get_voltage()
        csv_file.write(voltage + '\n')
        print(voltage + 'V :: ' + str(timer - x))
        x += 1
camera.stop_recording()
exit()
# ----------------------------------------
