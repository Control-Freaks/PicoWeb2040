import onewire, ds18x20, machine
from machine import Pin

def read_ds_sensor(gpio):
  ds_pin = Pin(gpio, Pin.IN)
  ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
  try:
    roms = ds_sensor.scan()
    # print('Found DS devices: ', roms)
    # print('Temperatures: ')
    ds_sensor.convert_temp()
    for rom in roms:
      temp = ds_sensor.read_temp(rom)
      if isinstance(temp, float):
        msg = round(temp, 2)
        return msg
  except:
    return '-100.0'
  
# print(read_ds_sensor(21))
  