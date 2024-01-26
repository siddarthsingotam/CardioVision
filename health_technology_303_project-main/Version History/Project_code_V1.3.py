from machine import ADC, Pin
import network
import time
from time import sleep
from ssd1306 import SSD1306_I2C
from piotimer import Piotimer
from fifo import Fifo
from filefifo import Filefifo
import urequests as requests
import ujson


width = 128
height = 64
i2c = machine.I2C(1,sda=machine.Pin(14), scl=machine.Pin(15), freq=400000)
oled = SSD1306_I2C(width, height, i2c)


ssid = "Enter your network ssid"
password = 'Enter password'


counter_1 = 0
max_limits = 5

def connect():
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    info = wlan.ifconfig()
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        oled.text('Waiting for connection...', 0, 10, 10)
        oled.show()
        sleep(1)
    if wlan.isconnected() == True:
        oled.text("Connected", 25, 15, 1)
        print(info[0])
        #oled.fill(0)
        oled.text(str(info[0]), 5, 30, 1)
        oled.show() 
try:
    connect()
except KeyboardInterrupt:
    machine.reset()
                    
sample_list = Fifo (1500)
adc = ADC(26)

samples = [] 
peaks = [] 
min_hr = 30
max_hr = 240
ppi_list = []
ppi_list_processed = []
interval_gap_ms = 4
counter = 0

def get_signal(dummy_variable_01): 
    sample_list.put(adc.read_u16())
    
    
#timer = Piotimer(period = 4, mode = Piotimer.PERIODIC, callback = get_signal)
sample_list = Filefifo('capture03_250Hz.txt')


while True: 
    if not sample_list.empty():
            measured = sample_list.get()
            samples.append(measured)
            if measured < 0:
                break
            if len(samples) >= 750:
                max_sample = max(samples)
                min_sample = min(samples)
                threshold = (3*max_sample + 2*min_sample)/5 
                
                prev = samples[0]
                counter = 0
                for s in samples:
                    if s >= threshold and prev < threshold:
                        peaks.append(counter)
                    counter += 1
                    prev = s
            
                for i in range(1, len(peaks)):
                    delta_gap = peaks[i] - peaks[i-1]
                    ppi = delta_gap * interval_gap_ms

                    if ppi > 0:
                         heart_rate = 60000/ppi
                         if heart_rate > min_hr and heart_rate < max_hr:
                             print(f'Heart Rate: {round(heart_rate)}')
                             oled.fill(0)
                             oled.text(f'HR:{round(heart_rate)} BPM',32 ,30, 1)
                             oled.show()
                             ppi_list.append(ppi)
                             ppi_list_processed = ppi_list[30:]
                    if len(ppi_list_processed) >= 25:
                            
                       break
                samples = [] 
                peaks = [] 
                
                    


    if len(ppi_list_processed) >= 25:
        break

oled.fill(0)
print('Processing...')
oled.show()

def calculate_hrv(ppi_list_processed):
   
    mean_ppi = sum(ppi_list_processed) / len(ppi_list_processed)
    
    
    mean_hr = 60000 / mean_ppi
    
    
    sdnn_sum = sum([(ppi - mean_ppi)**2 for ppi in ppi_list_processed])
    sdnn = (sdnn_sum / len(ppi_list_processed))**0.5
    
    
    rmssd_sum = sum([(ppi_list_processed[i+1] - ppi_list_processed[i])**2 for i in range(len(ppi_list_processed)-1)])
    rmssd = (rmssd_sum / (len(ppi_list_processed) - 1))**0.5
    
    return (mean_ppi, mean_hr, sdnn, rmssd)




APIKEY = "pbZRUi49X48I56oL1Lq8y8NDjq6rPfzX3AQeNo3a"
CLIENT_ID = "3pjgjdmamlj759te85icf0lucv"
CLIENT_SECRET = "111fqsli1eo7mejcrlffbklvftcnfl4keoadrdv1o45vt9pndlef"
LOGIN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/login"
TOKEN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/oauth2/token"
REDIRECT_URI = "https://analysis.kubioscloud.com/v1/portal/login"



response = requests.post(
    url=TOKEN_URL,
    data='grant_type=client_credentials&client_id={}'.format(CLIENT_ID),
    headers={'Content-Type': 'application/x-www-form-urlencoded'},
    auth=(CLIENT_ID, CLIENT_SECRET)
)
response = response.json()
access_token = response["access_token"]

intervals = ppi_list_processed
data_set = {
    "type": "RRI",
    "data": intervals,
    "analysis": {
        "type": "readiness"
    }
}


response = requests.post(
    url="https://analysis.kubioscloud.com/v2/analytics/analyze",
    headers={
        "Authorization": "Bearer {}".format(access_token),
        "X-Api-Key": APIKEY
    },
    json=data_set
)
response = response.json()



pns_index = response['analysis']['pns_index']
sns_index = response['analysis']['sns_index']
print("SNS value_Kubios: ", sns_index)
print("PNS value_kubios: ", pns_index)


sdnn_kubios_ms = response['analysis']['sdnn_ms']
rmssd_kubios_ms = response['analysis']['rmssd_ms']
mean_ppi, mean_hr, sdnn, rmssd = calculate_hrv(ppi_list)

import time

pages = [    {        'title': 'HRV Analysis',        'subtitle': 'by formulation',        'lines': [            "Mean PPI: {:.2f} ms".format(mean_ppi),            "Mean HR: {:.2f} bpm".format(mean_hr),            "SDNN: {:.2f} ms".format(sdnn),            "RMSSD: {:.2f} ms".format(rmssd)        ]
    },
    {
        'title': 'HRV Analysis',
        'subtitle': 'by Kubios',
        'lines': [
            "SDNN ms: {:.2f}".format(sdnn_kubios_ms),
            "RMSSD ms: {:.2f}".format(rmssd_kubios_ms),
            "SNS : {:.2f}".format(pns_index),
            "PNS : {:.2f}".format(sns_index)
        ]
    }
]

current_page = 0

while True:
    oled.fill(0)
    page = pages[current_page]
    oled.text(page['title'], 0, 0)
    oled.text(page['subtitle'], 0, 10)
    for i, line in enumerate(page['lines']):
        oled.text(line, 0, 20 + i * 10)
    oled.show()
    time.sleep(5)
    current_page = (current_page + 1) % len(pages)
