__version__ = "0.0.2" # fork by me on Dec 24, 2022 see bottom

# highly recommended to set a lowish garbage collection threshold
# to minimise memory fragmentation as we sometimes want to
# allocate relatively large blocks of ram.
import gc, os, machine
gc.threshold(50000)

# phew! the Pico (or Python) HTTP Endpoint Wrangler
from . import logging

# determine if remotely mounted or not, changes some behaviours like
# logging truncation
remote_mount = False
try:
  os.statvfs(".") # causes exception if remotely mounted (mpremote/pyboard.py)
except:
  remote_mount = True

def is_connected_to_wifi():
  import network, time
  wlan = network.WLAN(network.STA_IF)
  return wlan.isconnected()

# helper method to quickly get connected to wifi
def connect_to_wifi(ssid, password, timeout_seconds=30):
  import network, time

  statuses = {
    network.STAT_IDLE: "idle",
    network.STAT_CONNECTING: "connecting",
    network.STAT_WRONG_PASSWORD: "wrong password",
    network.STAT_NO_AP_FOUND: "access point not found",
    network.STAT_CONNECT_FAIL: "connection failed",
    network.STAT_GOT_IP: "got ip address"
  }

  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)    
  wlan.connect(ssid, password)
  start = time.ticks_ms()
  status = wlan.status()

  logging.debug(f"  - {statuses[status]}")
  while not wlan.isconnected() and (time.ticks_ms() - start) < (timeout_seconds * 1000):
    new_status = wlan.status()
    if status != new_status:
      logging.debug(f"  - {statuses[status]}")
      status = new_status
    time.sleep(0.25)

  if wlan.status() != 3:
    return None

  return wlan.ifconfig()[0]

# helper method to put the pico into access point mode
def access_point(ssid, password = None):
  import network

  # start up network in access point mode  
  wlan = network.WLAN(network.AP_IF)
  wlan.config(essid=ssid)
  if password:
    wlan.config(password=password)
  else:    
    wlan.config(security=0) # disable password
  wlan.active(True)

  return wlan

# some extra bits and peices I added =============== Dec 24, 2022
# return network ip
def ifconf():
  import network
  wlan = network.WLAN(network.STA_IF)
  return wlan.ifconfig()

# scan and return all visible APs
def apscan():
  import network
  wlan = network.WLAN(network.STA_IF)
  wlan.scan()
  return wlan.scan()

# get rssi by ssid (picks first instance) or best get by bssid
# use bytestring form b''
def aprssi():
  import network
  wlan = network.WLAN(network.STA_IF)
  # wlan.scan()
  try:
    scan = wlan.scan()
    rssi = (scan[0])[3]  # grab first rssi on list
  except:
    rssi = 0
  return rssi  
    
def pico_mac():
  import ubinascii
  import network
  wlan = network.WLAN(network.STA_IF)
  mac = ubinascii.hexlify(wlan.config('mac'), ':').decode()
  return mac

def pico_esn():
  import ubinascii  
  # client_id = ubinascii.hexlify(machine.unique_id())
  client_id = ubinascii.hexlify(machine.unique_id(), ':').decode()
  return client_id