import network
import socket
import time
from time import sleep
from machine import Pin, I2C
from machine import ADC
from ssd1306 import SSD1306_I2C
import bme280
import utime

ssid = '' #Your network name
password = '' #Yourd

pin = Pin("LED", Pin.OUT)
#relay = Pin(18, Pin.OUT)
#readDelay = 0.5
soil = ADC(Pin(28))
soil1 = ADC(Pin(27))
soil2 = ADC(Pin(26))

sensor_temp = machine.ADC(machine.ADC.CORE_TEMP)
conversion_factor = 3.3 / (65535)

led_onboard = machine.Pin(25, machine.Pin.OUT)
led_onboard.value(0)

rtc=machine.RTC()

min_moisture=19200
max_moisture=49300
 
i2c=I2C(0,sda=Pin(0), scl=Pin(1), freq=400000)
oled = SSD1306_I2C(128,64,i2c=i2c, addr = 60) 
bme = bme280.BME280(i2c=i2c, addr = 118) 

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

def webpage(reading, Tempz, Humidiz, Pressurez, Moisturez1, Moisturez2, Moisturez3):
    #Template HTML
    html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <title>ROBO-GRO</title>
            <meta http-equiv="refresh" content="1">
            </head>
            <body style="background-color:#3d4658">
            <h1 style="color: rgb(169, 250, 48);
            font-family: Arial, Helvetica, sans-serif;
            font-size: 60px;
            font-weight: 200;
            text-decoration:underline;
            text-align: center;">ROBO-GRO
            </h1>
            <br>
            <table style="width:100%;
            color: rgba(163, 20, 220, 0.95);
            font-family: Arial, Helvetica, sans-serif;
            font-size: 30px;
            font-weight: 100;
            text-align: left;
            background-color: #9ea0b7;">
            <tr>
            <th>Date & Time</th>
            <th>Temp</th>
            <th>Humidity</th>
            <th>Pressure</th>
            <th>Station 1</th>
            <th>Station 2</th>
            <th>Station 3</th>
            </tr>
            <tr>
            <td>{reading}</td>
            <td>{Tempz}</td>
            <td>{Humidiz}</td>
            <td>{Pressurez}</td>
            <td>{Moisturez1}</td>
            <td>{Moisturez2}</td>
            <td>{Moisturez3}</td>
            </tr>
            </table>
            </body>
            </html>
            """
    return str(html)
   
def serve(connection):
    #Start a web server
   
    while True:
        time.sleep(1)
        pin.toggle()
       
        #file=open("data4.csv","a")
        bme = bme280.BME280(i2c=i2c)
        temp = bme.values[0]
        pressure = bme.values[1]
        humidity = bme.values[2]
        timestamp=rtc.datetime()
        moisture = (max_moisture-soil.read_u16())*100/(max_moisture-min_moisture)
        moisture1 = (max_moisture-soil1.read_u16())*100/(max_moisture-min_moisture)
        moisture2 = (max_moisture-soil2.read_u16())*100/(max_moisture-min_moisture)
        reader = sensor_temp.read_u16() * conversion_factor
        temperature = 27 - (reader - 0.706)/0.001721
        timestring="%04d-%02d-%02d %02d:%02d:%02d"%(timestamp[0:3] +
                                                timestamp[4:7])
        reading = 'Date and time:  ' + str(timestring) + '\n'
        Tempz ='Temperature: ' + str(temp) + '\n'
        Humidiz = 'Humidity: ' + str(humidity) + '\n'
        Pressurez = 'Pressure: ' + str(pressure) + '\n'
        Moisturez1 = 'Station 1: ' + str(moisture) + '\n'
        Moisturez2 = 'Station 2: ' + str(moisture1) + '\n'
        Moisturez3 = 'Station 3: ' + str(moisture2) + '\n'
        print(reading)
        print(Tempz)
        print(Humidiz)
        print(Pressurez)
        print(Moisturez1)
        print(Moisturez2)
        print(Moisturez3)
        oled.fill(0)
        oled.text("Temp: ",10,00)
        oled.text(str(temp),50,00)
        oled.text("*C",90,00)
        oled.text("Humi: ",10,15)
        oled.text(str(humidity),50,15)
        oled.text("%",90,15)
        oled.text("M1: ",10,30)
        oled.text(str(moisture),40,30)
        oled.text("%",90,30)
        oled.text("M2: ",10,43)
        oled.text(str(moisture1),40,43)
        oled.text("%",90,43)
        oled.text("M3: ",10,57)
        oled.text(str(moisture2),40,57)
        oled.text("%",90,57)
        oled.show()
       
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)      
        html = webpage(reading, Tempz, Humidiz, Pressurez, Moisturez1, Moisturez2, Moisturez3)
        client.send(html)
        led_onboard.value(1)
        led_onboard.value(0)
       
        if moisture <= 70.0:
            relay = Pin(18, Pin.OUT)
            readDelay = 1
            relay.value(0)
            print('On')
            utime.sleep(2)
            print('Off')
            relay.value(1)
            print('On')
            utime.sleep(2)
            print('Off')
            utime.sleep(1)
            utime.sleep(readDelay)
        else:
            print("Station1 is Moist Captain!")
            
        
        if moisture1 <= 70.0:
            relay = Pin(14, Pin.OUT)
            readDelay = 1
            relay.value(0)
            print('On')
            utime.sleep(2)
            print('Off')
            relay.value(1)
            print('On')
            utime.sleep(2)
            print('Off')
            utime.sleep(1)
            utime.sleep(readDelay)
        else:
            print("Station2 is Moist Captain!")
            
        if moisture2 <= 70.0:
            relay = Pin(10, Pin.OUT)
            readDelay = 1
            relay.value(0)
            print('On')
            utime.sleep(2)
            print('Off')
            relay.value(1)
            print('On')
            utime.sleep(2)
            print('Off')
            utime.sleep(1)
            utime.sleep(readDelay)
        else:
            print("Station3 is Moist Captain!")
        client.close()    

try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()
