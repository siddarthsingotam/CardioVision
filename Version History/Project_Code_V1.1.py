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

# Hard ware items
width = 128
height = 64
i2c = machine.I2C(1,sda=machine.Pin(14), scl=machine.Pin(15), freq=400000)
oled = SSD1306_I2C(width, height, i2c)

# Connection items
ssid = "Enter your network ssid"
password = 'Enter password'

# Runners and counters
counter_1 = 0
max_limits = 5

def connect():
    #Connect to WLAN
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
                    
sample_list = Fifo (1500)#ring-buffer size 60
adc = ADC(26)#Connected sensor to ADC_0 slot polled pin 26 to convert analog signals

samples = [] #collecting samples
peaks = [] #collecting peaks from the samples
min_hr = 30
max_hr = 240
ppi_list = []
interval_gap_ms = 4

def get_signal(dummy_variable_01): #Putting ADC values in fifo of size 60 and getsignal is a callback function.
    sample_list.put(adc.read_u16())
    
    
#timer = Piotimer(period = 4, mode = Piotimer.PERIODIC, callback = get_signal)#Period = 4, for 250Hz sampling rate 

sample_list = Filefifo('capture03_250Hz.txt')


while True: #Reading ADC values (16 bit range values), we can set a specific ADC value to detect change; i.e rise/fall of in peak measured from the sensor
    if not sample_list.empty():
            measured = sample_list.get()
            samples.append(measured)
            if measured < 0:
                break
            if len(samples) >= 750:
                max_sample = max(samples)
                min_sample = min(samples)
                threshold = (3*max_sample + 2*min_sample)/5 # setting threshold
                
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
                    if len(ppi_list) >= 25:
                        break
                samples = [] #Clearing out ADC samples to refresh
                peaks = [] #Clearing out peaks to refresh counters
                 
                    


    if len(ppi_list) >= 25:
        break

# Clear display

oled.fill(0)
def calculate_hrv(ppi_list):
    # Calculate mean PPI
    mean_ppi = sum(ppi_list) / len(ppi_list)
    
    # Calculate mean HR
    mean_hr = 60000 / mean_ppi
    
    # Calculate SDNN
    sdnn_sum = sum([(ppi - mean_ppi)**2 for ppi in ppi_list])
    sdnn = (sdnn_sum / len(ppi_list))**0.5
    
    # Calculate RMSSD
    rmssd_sum = sum([(ppi_list[i+1] - ppi_list[i])**2 for i in range(len(ppi_list)-1)])
    rmssd = (rmssd_sum / (len(ppi_list) - 1))**0.5
    
    return (mean_ppi, mean_hr, sdnn, rmssd)




APIKEY = "pbZRUi49X48I56oL1Lq8y8NDjq6rPfzX3AQeNo3a"
CLIENT_ID = "3pjgjdmamlj759te85icf0lucv"
CLIENT_SECRET = "111fqsli1eo7mejcrlffbklvftcnfl4keoadrdv1o45vt9pndlef"
LOGIN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/login"
TOKEN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/oauth2/token"
REDIRECT_URI = "https://analysis.kubioscloud.com/v1/portal/login"


# Get access token
response = requests.post(
    url=TOKEN_URL,
    data='grant_type=client_credentials&client_id={}'.format(CLIENT_ID),
    headers={'Content-Type': 'application/x-www-form-urlencoded'},
    auth=(CLIENT_ID, CLIENT_SECRET)
)
response = response.json()
access_token = response["access_token"]

intervals = ppi_list
data_set = {
    "type": "RRI",
    "data": intervals,
    "analysis": {
        "type": "readiness"
    }
}

# Make the readiness analysis with the given data
response = requests.post(
    url="https://analysis.kubioscloud.com/v2/analytics/analyze",
    headers={
        "Authorization": "Bearer {}".format(access_token),
        "X-Api-Key": APIKEY
    },
    json=data_set
)
response = response.json()

#print(response)


# Print out the SNS and PNS values on the OLED screen

pns_index = response['analysis']['pns_index']
sns_index = response['analysis']['sns_index']
print("SNS value_Kubios: ", sns_index)
print("PNS value_kubios: ", pns_index)

# Display sdnn_ms and rmssd_ms values on the OLED screen
sdnn_kubios_ms = response['analysis']['sdnn_ms']
rmssd_kubios_ms = response['analysis']['rmssd_ms']

def display_results(mean_ppi, mean_hr, sdnn, rmssd):
    oled.fill(0)
    oled.text("HRV Analysis", 0, 0)
    oled.text("by formulation", 0, 10)
    oled.text("Mean PPI: {:.2f} ms".format(mean_ppi), 0, 20)
    oled.text("Mean HR: {:.2f} bpm".format(mean_hr), 0, 30)
    oled.text("SDNN: {:.2f} ms".format(sdnn), 0, 40)
    oled.text("RMSSD: {:.2f} ms".format(rmssd), 0, 50)
    oled.show()
    sleep(5)
    oled.fill(0)    
    oled.text("by Kubios", 0, 10, 10)
    oled.text("SDNN ms: {:.2f}".format(sdnn_kubios_ms), 0, 20, 10)
    oled.text("RMSSD ms: {:.2f}".format(rmssd_kubios_ms), 0, 30, 10)
    oled.show()
#Display SNS and PNS values on the OLED screen
    oled.text("SNS : {:.2f}".format(pns_index), 0, 40, 10)
    oled.text("PNS : {:.2f}".format(sns_index), 0, 50, 10)
    oled.show()
while True:
    # Calculate and display results for  ppi_list
    mean_ppi, mean_hr, sdnn, rmssd = calculate_hrv(ppi_list)
    display_results(mean_ppi, mean_hr, sdnn, rmssd)
    sleep(5)
    mean_ppi, mean_hr, sdnn, rmssd = calculate_hrv(ppi_list)
    display_results(mean_ppi, mean_hr, sdnn_kubios_ms, rmssd_kubios_ms)
     
