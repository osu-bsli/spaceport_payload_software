# imports
# -------
import time
from picamera2.encoders import H264Encoder
from picamera2 import Picamera2
from smbus import SMBus
import random
# -------


def twos_comp(val, bits):
# compute the 2's complement of int value val
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is

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
    # get 8 least significant bits (last 4 will always be 0)
    dataLSB = bus.read_byte_data(ACCELEROMETER_REGISTER, LSB)
    # get 8 most significant bits
    dataMSB = bus.read_byte_data(ACCELEROMETER_REGISTER, MSB)
    # convert data to single 12-bit number
    accl = ((dataMSB) * 256) + dataLSB
    accl >>= 4
    # convert from twos-complement to decimal
    accl = twos_comp(accl, 12)
    # final value to the nearest G
    accl /= 5
    return accl
# -----------------------------

# check acceleration
acceleration = 0
# check if acceleration in any direction is greater than 5gs
while(acceleration <= 5)
    x_acc = get_acc(ACC_DATA[0],ACC_DATA[1])
    y_acc = get_acc(ACC_DATA[2],ACC_DATA[3])
    z_acc = get_acc(ACC_DATA[4],ACC_DATA[5])
    acceleration = max(x_acc, y_acc, z_acc)

# start recording / capturing voltage data
# ----------------------------------------
# start a timer
timer = time.process_time()

# set value for timer stop
timer_stop = (15 * 60.0)
camera.start_recording(encoder, output)
with open('voltage_data.csv', "a", newline='') as csv_file:
    current_time = 0
    while current_time < timer_stop :
        voltage = get_voltage()
        csv_file.write(voltage + '\n')
        print(voltage + 'V :: ' + str(timer - x))
        current_time = time.process_time() - timer
camera.stop_recording()
exit()
# ----------------------------------------
