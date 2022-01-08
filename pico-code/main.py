from machine import Pin, UART, I2C
from utime import ticks_ms, sleep
import time
import sdcard
import uos
from my_helper import *
from adafruit_gps import *
from gps_class import *
import _thread

# Load up the microSD card for mass storage
#--------------------------------------------------#

## Assign chip select (CS) pin (and start it high)
cs = machine.Pin(15, machine.Pin.OUT)

## Intialize SPI peripheral (start with 1 MHz)
spi = machine.SPI(1,
                  baudrate=1000000,
                  polarity=0,
                  phase=0,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=machine.Pin(10),
                  mosi=machine.Pin(11),
                  miso=machine.Pin(12))

## Initialize SD card
sd = sdcard.SDCard(spi, cs)

## Mount filesystem
vfs = uos.VfsFat(sd)
uos.mount(vfs, "/sd")

#--------------------------------------------------#

# GPS and GPSm Object
gps_module = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))
gps = GPS(gps_module)
gps_m = GPSm(gps_module)

# Modem Object
modem = UART(0, 115200)
modem_pwr = Pin(14, Pin.OUT)
led = Pin(25, Pin.OUT)
modem = Modem(modem, modem_pwr, led)

# Start the modem
modem.startup()

# Configure GPS
gps.send_command("PMTK161,1") # Awake
time.sleep(10)
gps.send_command("PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0") # Only RMC
time.sleep(6) # Give 10 minutes to fix in indoor setting

'''
Process commands and send responses via SMS accordingly
'''
def process_cmd(modem, gps, gps_m):
    print("Checking if useful commands have been sent ...")
    if "Stop tracking" in modem.command:
        modem.track = False
        modem.command = ""
        modem.send_sms("Stopped tracking!")
        print("Stopped tracking!")
    elif "Begin tracking" in modem.command or modem.track:
        modem.track = True
        modem.command = ""
        if gps_m.sleep:
            gps.send_cmd("PMTK161,1")
            time.sleep(10)
            gps_m.sleep = False
        gps_info = gps_m.get_rmc()
        if gps_info:
            modem.send_sms("Device is currently at {} {}".format(gps_info[2], gps_info[3]))
            print("Device is currently at {} {}".format(gps_info[2], gps_info[3]))
        else:
            modem.send_sms("These are fake coordinates for presentation purposes. 0000 N 0000 W")
            print("These are fake coordinates for presentation purposes. 0000 N 0000 W")
    elif "Battery percentage" in modem.command:
        modem.command = ""
        batt_percent = modem.batt_percent()
        modem.send_sms("The battery percentage is {}%".format(batt_percent))
        print("The battery percentage is {}%".format(batt_percent))
        
'''
Saves coordinates to csv file
'''
def normal_mode(modem, gps, gps_m):
    while True:
        if gps_m.sleep:
            gps.send_command("PMTK161,1")
            time.sleep(10)
            gps_m.sleep = False
        modem.check_sms()
        process_cmd(modem, gps, gps_m)
        time.sleep(0.5)
        values = gps_m.get_rmc()
        print(values)
        gps.send_command("PMTK161,0")
        time.sleep(10)
        gps_m.sleep = True
        if values != None:
        # Create a file and write something to it
            with open("/sd/december_data.csv", "a") as file:
                file.write("{}, {}, {}, {}\r\n".format(values[0], values[1], values[2], values[3]))
        time.sleep(10) # roughly every 10 minutes

normal_mode(modem, gps, gps_m)


