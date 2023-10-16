# Power interruption during slow blink will switch picoweb into 'ap' mode on following.
# power up. Picoweb will run in 'ap' mode for 5 minutes before rebooting into "sta" mode
import time
import machine
import sys

led = machine.Pin("LED", machine.Pin.OUT); led.off()

'''====================== AP Option ======================='''
try:
    from power_up_record import last_power_up
    print('last_power_up =',last_power_up)

    if last_power_up == 'interrupted':      
        
        for i in range(10):
            led.on()
            time.sleep(.02)
            led.off()
            time.sleep(.2)

        with open('power_up_record.py','w') as file:
            file.write("last_power_up = 'clean'")

        with open('picoweb_mode.py','w') as file:
            file.write("mode = 'ap'")
        
        print("importing picoweb: mode = 'ap'")
        import picoweb
        
except:
    pass

''' ==================== STA Option ========================='''

with open('power_up_record.py','w') as file: # write file
    file.write("last_power_up = 'interrupted'")

for i in range(10):
    led.on()
    time.sleep(.1)
    led.off()
    time.sleep(.9)

with open('power_up_record.py','w') as file: # write file
    file.write("last_power_up = 'clean'")
    
with open('picoweb_mode.py','w') as file: # write file
    file.write("mode = 'sta'")    

print("importing picoweb: mode = 'sta'")
import picoweb

  
