from machine import Pin, I2C
from time import sleep
from struct import unpack as unp

i2c = I2C(0, scl=Pin(13), sda=Pin(12), freq=100000)
# i2c.scan()  # sht20 scan = [64]

# SHT20 default address
SHT20_I2CADDR = 64

# SHT20 Commands
TRI_T_MEASURE_NO_HOLD = b'\xf3'
TRI_RH_MEASURE_NO_HOLD = b'\xf5'
READ_USER_REG = b'\xe7'
WRITE_USER_REG = b'\xe6'
SOFT_RESET = b'\xfe'


def get_temperature():
    try:       
        i2c.writeto(SHT20_I2CADDR, TRI_T_MEASURE_NO_HOLD)
        sleep(.150)
        origin_data = i2c.readfrom(SHT20_I2CADDR, 2)
        origin_value = unp('>h', origin_data)[0]
        value = -46.85 + 175.72 * (origin_value / 65536)
        value = round(value, 2)
        return str(value)
    except:
        return 'no_sht20'
    
def get_humidity():
    try:
        i2c.writeto(SHT20_I2CADDR, TRI_RH_MEASURE_NO_HOLD)
        sleep(.150)
        origin_data = i2c.readfrom(SHT20_I2CADDR, 2)
        origin_value = unp('>H', origin_data)[0]
        value = -6 + 125 * (origin_value / 65536)
        value = round(value, 2)
        return str(value)  
    except:
        return 'no_sht20'