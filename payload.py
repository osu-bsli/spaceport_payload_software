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

# Accelerometer setup
# -------------------
ACCELEROMETER_REGISTER = 0xFA
ACC_DATA = [0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D] # X, X, Y, Y, Z, Z
# First byte is 8 MSB, 2nd bit is 4 LSB
# -------------------

# Function to run ADC
# -------------------
def get_voltage():
    data = bus.read_i2c_block_data(ADC_REGISTER, 0x00, 2) # read two bytes back from 0x00
    voltage = (data[0] & 0x0F) * 256 + data[1] # convert value into voltage
    if voltage > 2047:
        voltage -= 4095 # handle overflow
    return voltage
# -------------------

# Function to run accelerometer
# -----------------------------
def get_acc(MSB, LSB):
    dataLSB = bus.read_byte_data(ACCELEROMETER_REGISTER, LSB)
    dataMSB = bus.read_byte_data(ACCELEROMETER_REGISTER, MSB)
    # convert data to 10 bits
    accl = ((dataMSB) * 256) + dataLSB
    accl >>= 4
    if accl > 511:
        accl -= 1024
    return accl
# -----------------------------
    
# bool FLIGHT = False # Flight status
timer = 60

# check acceleration
acceleration = 0
while(acceleration <= 5):
    x_acc = get_acc(ACC_DATA[0],ACC_DATA[1])
    y_acc = get_acc(ACC_DATA[2],ACC_DATA[3])
    z_acc = get_acc(ACC_DATA[4],ACC_DATA[5])
    acceleration = max(x_acc, y_acc, z_acc)

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
