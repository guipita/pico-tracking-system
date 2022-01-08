from machine import UART, Pin, I2C
from utime import ticks_ms, sleep
import time
import uasyncio

class Modem():

    def __init__(self, modem, pwr_pin, led_pin):
        self.modem = modem
        self.led_pin = led_pin
        self.pwr_pin = pwr_pin
        self.command = ""
        self.track = False

    '''
    Send an AT command and compare to desired response. True if desired
    response. False if not desired response
    '''
    def send_at_compare(self, cmd, check="OK", timeout=1000):
        response = self.send_at_get(cmd, timeout)
        if len(response) > 0 and check in response:
            return True
        return False

    '''
    Send an AT command and return response
    '''
    def send_at_get(self, cmd, timeout=1000):
        self.send_at(cmd)
        return self.read(timeout)

    '''
    Send an AT command
    '''
    def send_at(self, cmd):
        self.modem.write((cmd + "\r\n").encode())

    '''
    Read response via RX pin on Pi Pico from modem
    '''
    def read(self, timeout=1000):
        response = bytes()
        now = ticks_ms()
        while (ticks_ms() - now) < timeout and len(response) < 1025:
            if self.modem.any():
                response += self.modem.read(1)
        return response.decode()

    '''
    Check if modem is powered on; if not, power on
    '''
    def boot_modem(self):
        print("Booting modem ...")
        i = 0
        while i < 30:
            if self.send_at_compare(cmd="ATE1"):
                print("The modem is ready")
                return True
            if i != 0 and i%10 == 0:
                print("Switching modem power state ...")
                self.switch_power_state()
                time.sleep(10)
            time.sleep(4)
            i += 1
        return False

    '''
    Switch power state of module
    '''
    def switch_power_state(self):
        self.pwr_pin.value(1)
        sleep(1.5)
        self.pwr_pin.value(0)

    '''
    Check we are connected to network
    '''
    def check_network(self):
        i = 0
        while i < 100:
            response = self.send_at_get(cmd="AT+COPS?")
            lines = self.split_response(response)
            if "+COPS:" in lines[1] and "," in lines[1]:
                print("Network Information: {}".format(lines[1].strip("+COPS: ")))
                return True
        return False
                
    '''
    Configure modem for network connectivity
    '''
    def configure_modem(self):
        # AT commands can be sent together, not just one at a time.
        # Set the error reporting level, set SMS text mode, delete left-over SMS
        # select LTE-only mode, select Cat-M only mode, set the APN to 'super' for Super SIM
        self.send_at_compare(cmd="AT+CMEE=2;+CMGF=1;+CMGD=,4;+CNMP=38;+CMNB=1;+CGDCONT=1,\"IP\",\"super\"")
        print("Modem configured for Cat-M and Super SIM")

    def led_on(self):
        self.led_pin.value(1)

    def led_off(self):
        self.led_pin.value(0)

    '''
    Split a response from the modem and return the non-empty lines in a
    list
    '''
    def split_response(self, response):
        result = []
        lines = response.split("\r\n")
        for line in lines:
            if len(line) > 0:
                result.append(line)
        return result

    '''
    Start-up procedure for modem
    '''
    def startup(self):
        if self.boot_modem():
            self.configure_modem()
            # Check if we're attached
            if self.check_network():
                self.led_on()
                time.sleep(5)
                self.led_off()
            else:
                print("Not attached to network")
                for i in range(3):
                    self.led_on()
                    time.sleep(1)
                    self.led_off()

    '''
    Check if received an SMS from intended number, and return SMS
    '''
    def check_sms(self, intend_num="0"):
        sms = self.send_at_get("AT+CMGR=" + intend_num, 2000)
        if "REC UNREAD" in sms:
            self.command = self.split_response(sms)[-2]
            print(self.command)
            self.send_at("AT+CMGD=,4")
            time.sleep(2)

    '''
    Debug AT Commands
    '''
    def debug(self):
        while True:
            value = input("Enter AT Command: ")
            if value == "end":
                print("Terminated")
                break
            print(self.send_at_get(value))

    '''
    Get battery percentage
    '''
    def batt_percent(self):
        response = self.send_at_get("AT+CBC")
        lines = self.split_response(response)
        for line in lines:
            if "+CBC:" in line:
                return line.split(",")[1]

    '''
    Send SMS
    '''
    def send_sms(self, cmd, phone_num = "000"):
        if self.send_at_compare("AT+CMGS=\"{}\"".format(phone_num), ">"):
            self.send_at(cmd + chr(26))
            time.sleep(5)