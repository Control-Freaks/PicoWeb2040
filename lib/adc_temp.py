import machine
import utime
from secret import ADC_VREF


def Temp():
    try:
        sensor_temp = machine.ADC(4) 
        # conversion_factor = 2.5 / (65535)  # 2.5V ADC_VREF
        # conversion_factor = 3.3 / (65535)  # 3.3V ADC_VREF
        conversion_factor = ADC_VREF / (65535)
        Temp=0
        for i in range(0,10):
            read = sensor_temp.read_u16() * conversion_factor
            temp = 27 - (read - 0.706)/0.001721
            
            utime.sleep(.01)
            Temp=temp+Temp
        Temp = Temp/10 
        Temp = round(Temp, 2)
        return Temp   
    except:
        return -100.00


# print(Temp())