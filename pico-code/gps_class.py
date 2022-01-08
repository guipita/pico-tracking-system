from machine import UART, Pin, I2C
from utime import ticks_ms, sleep
import time

class GPSm():

    def __init__(self, modem):
        self.modem = modem
        self.sleep = False
    
    def get_rmc(self):
        current = ticks_ms()
        while ticks_ms() - current <= 60000:
            time.sleep(0.2)
            data = str(self.modem.readline()).split(',')
            try:
                assert "RMC" in data[0]
                assert len(data) == 13
                latitude = float(data[3])
                longitude = float(data[5])
                date = data[9]
                utc_time = data[1][0] + data[1][1] + ":" + data[1][2] + data[1][3] + ":" + data[1][4] + data[1][5]
                if data[4] == "S":
                    latitude *= -1
                if data[6] == "W":
                    longitude *= -1
                return date, utc_time, latitude, longitude
            except:
                continue
        return None
