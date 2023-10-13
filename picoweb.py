# https://github.com/pimoroni/phew/blob/main/README.md#add_route
# Added a few functions to the original phew (link above) for this project!
# Transmit editor works well for FTP file transfer
# Drag and drop> rp2-pico-w-20221220-unstable-v1.19.1-782-g699477d12.uf2
from phew import connect_to_wifi,access_point,logging,server,ifconf,apscan,pico_mac,aprssi,ntp 
from phew.template import render_template
from phew.logging import datetime_string
from secret import ssid,password,server_name,location
from sht20 import get_temperature, get_humidity
from ds_temp import read_ds_sensor
from adc_temp import Temp
from machine import Pin,ADC,Timer,reset 
import time
import _thread

# set pin functions
led = Pin('LED', Pin.OUT); led.off()

in0  = Pin(21, Pin.IN)
out0 = Pin(20, Pin.OUT); led.off() # led.off ????
in1  = Pin(19, Pin.IN)
out1 = Pin(18, Pin.OUT); led.off()      
in2  = Pin(17, Pin.IN)
out2 = Pin(16, Pin.OUT); led.off()               
in3  = Pin(15, Pin.IN)
out3 = Pin(14, Pin.OUT); led.off()

ADC0 = ADC(0)
ADC1 = ADC(1)
ADC2 = ADC(2)

# define timer_0 callback 
tim = Timer()
def tick(timer):
    print('timer_0 ran out')
    delayed_reboot()
# tim.init(period=300000, mode=Timer.ONE_SHOT, callback=tick) # 5 minutes
# tim.init(period=900000, mode=Timer.ONE_SHOT, callback=tick) # 15 minutes
tim.init(period=1200000, mode=Timer.ONE_SHOT, callback=tick) # 20 minutes

MAC=pico_mac()
short_mac = MAC[-5:]                                
ap_ssid = 'PicoWeb-' + short_mac.replace(':', '')   

# import operating mode
try:
    from picoweb_mode import mode
    if mode == 'ap':                             
        access_point(ap_ssid, password=None)           
        #  ifconfig=ifconf()
        ip = '192.168.4.1'  # ip=ifconfig[0]
        tim.init(period=300000, mode=Timer.ONE_SHOT, callback=tick) # 5 minutes
    else:                                             
        connect_to_wifi(ssid, password)                 
        ifconfig=ifconf()
        ip=ifconfig[0]
# exception if module is missing or malformed        
except:
    connect_to_wifi(ssid, password)                 
    ifconfig=ifconf()
    ip=ifconfig[0]
    
# load one time variables
logging.debug('> IP', ip)
logging.debug('> APSCAN', apscan())
logging.debug('ifconf:', ifconf())
logging.debug('NTP:', ntp.fetch(synch_with_rtc=True, timeout=10))  # sync to ntp and log 
start_time=datetime_string()  # grab at startup only 
gps=location


def get_outputs():
    global Output_0, Output_1, Output_2
    
    Output_0 = in0.value()
    if Output_0 == 1:
        Output_0 = 'On'
    else:
        Output_0 = 'Off'

    Output_1 = in1.value()
    if Output_1 == 1:
        Output_1 = 'On'
    else:
        Output_1 = 'Off'      
    
    Output_2 = in2.value()
    if Output_2 == 1:
        Output_2 = 'On'
    else:
        Output_2 = 'Off'
        
        
def get_adcs():
    global ADC_0, ADC_1, ADC_2
    
    a=0
    for i in range(16):  
        adc_0 = ADC0.read_u16()
        time.sleep(.001)  # (2us per read*16) + .001sec*16  = .0167 one ac cycle 
        a = a + adc_0
    ADC_0 = str(int(a/16))

    a=0
    for i in range(16):
        adc_1 = ADC1.read_u16()
        time.sleep(.001)        
        a = a + adc_1
    ADC_1 = str(int(a/16))

    a=0
    for i in range(16):
        adc_2 = ADC2.read_u16()
        time.sleep(.001)        
        a = a + adc_2
    ADC_2 = str(int(a/16))
get_adcs()


def get_sht20():
    global t_sht20, rh_sht20
    t_sht20  = get_temperature()
    rh_sht20 = get_humidity()
    # print(t_sht20), print(rh_sht20)
get_sht20()


def delayed_reboot():
    print('rebooting in 8 seconds')
    time.sleep(8)
    reset()

def delayed_stop_server():
    print('killing HTTP in 10 seconds')
    time.sleep(10)
    server.stop()  # kill http server here <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    
def get_slow_stuff():
    global temp1, temp2, rssi 
    temp1=str(read_ds_sensor(22))
    temp2=str(Temp())  #  .7 second read time
    rssi=str(aprssi()) #  .5 second read time  
get_slow_stuff()


def template():
    led.on()
    tim.init(period=1200000, mode=Timer.ONE_SHOT, callback=tick) # new May-30-2023
    get_outputs()
    get_adcs()
    get_sht20()  # <<< new addition Apr-11-2023
    get_slow_stuff()  
    led.off()    
    return {'gps':location,'header':server_name,'mac':MAC,'time':start_time,'tempA':temp1,
            'tempB':temp2,'signal':rssi,'adc0':ADC_0,'adc1':ADC_1,'adc2':ADC_2,'myip':ip,
            'State_0':Output_0, 'State_1':Output_1, 'State_2':Output_2,'T_sht20':t_sht20,
            'RH_sht20':rh_sht20}



# landing page login
@server.route('/', ['POST','GET'])
def login_form(request):
    print(request.method)
    if request.method == 'GET':
        return render_template('/html/login.html', myip=ip)
    if request.method == 'POST':    
        username = request.form.get('username', None)
        password = request.form.get('password', None)

        if username == 'picoweb' and password == '12345678':             
            return render_template('/html/index.html',**template())
        else:          
            return render_template('/html/login.html',**template())


# index - forwarded here from login page - no re-login on page refresh
@server.route('/index_PWxHb44hqTXumXIykgDS')
def index(request):    
    return render_template('/html/index.html',**template())



# serve up simple data for M2M server/clients *NodeRed etc
@server.route('/data')
def index(request):    
    return render_template('/html/data.html',**template())



# toggle_0 and update page
@server.route('/out0_toggle_PWxHb44hqTXumXIykgDS')
def index(request):    
    out0.toggle()
    return render_template('/html/index.html',**template())

# out0_on and update page
@server.route('/out0_on_PWxHb44hqTXumXIykgDS')
def index(request):    
    out0.on()
    return render_template('/html/data.html',**template())

# out0_off and update page
@server.route('/out0_off_PWxHb44hqTXumXIykgDS')
def index(request):    
    out0.off()
    return render_template('/html/data.html',**template())



# toggle_1 and update page
@server.route('/out1_toggle_PWxHb44hqTXumXIykgDS')
def index(request):    
    out1.toggle()
    return render_template('/html/index.html',**template())

# out1_on and update page
@server.route('/out1_on_PWxHb44hqTXumXIykgDS')
def index(request):    
    out1.on()
    return render_template('/html/data.html',**template())

# out1_off and update page
@server.route('/out1_off_PWxHb44hqTXumXIykgDS')
def index(request):    
    out1.off()
    return render_template('/html/data.html',**template())



# toggle_2 and update page
@server.route('/out2_toggle_PWxHb44hqTXumXIykgDS')
def index(request):    
    out2.toggle()
    return render_template('/html/index.html',**template())

# out2_on and update page
@server.route('/out2_on_PWxHb44hqTXumXIykgDS')
def index(request):    
    out2.on()
    return render_template('/html/data.html',**template())

# out2_off and update page
@server.route('/out2_off_PWxHb44hqTXumXIykgDS')
def index(request):    
    out2.off()
    return render_template('/html/data.html',**template())


# request: start ftp server
@server.route('/ftp_PWxHb44hqTXumXIykgDS')
def index(request):    
    # try:
    tim.init(period=900000, mode=Timer.ONE_SHOT, callback=tick) # 15 minutes
    import uftpd        
    return render_template('/html/index_ftp.html',**template(),ftp='')
    # finally:
        # _thread.start_new_thread(delayed_stop_server, ())
        

# request: reboot sequence
@server.route('/reboot_PWxHb44hqTXumXIykgDS')
def index(request):    
    try:
        return render_template('/html/index_reboot.html',**template(),reboot='')
    finally:
        _thread.start_new_thread(delayed_reboot, ())



# image file server 
@server.route('/images/<fn>')
def images(req, fn):
    led.on()
    time.sleep(.1)
    led.off()
    return server.serve_file('/images/{}'.format(fn))



# log.csv file server <<<<<<<<<<<<<<<< hacky but, using .csv because .txt is not formatting
@server.route('/log_PWxHb44hqTXumXIykgDS')
def images(req):
    led.on()
    time.sleep(.1)
    led.off()
    return server.serve_file('/log.txt')



@server.catchall()
def catchall(request):
    led.on()
    time.sleep(.1)
    led.off()
    return 'Not found', 404


server.run()
