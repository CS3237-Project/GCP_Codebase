import base64
from datetime import datetime
from pathlib import Path
import os
import os.path
import glob
import imageProcessor
import threading
import paho.mqtt.client as mqtt
import struct
import math
import warnings
import pytz
from termcolor import colored

warnings.filterwarnings("ignore")

IMAGE_FOLDER_PATH = '/home/pratyushghosh14/inputImages/'
JSON_FOLDER_PATH = '/home/pratyushghosh14/outputJSONs/'
OUTPUT_FOLDER_PATH = '/home/pratyushghosh14/outputImages/'
CVA_THRESHOLD_LO = 40.0
CVA_THRESHOLD_HI = 65.0
host_ip = '34.81.217.13'  # Broker IP
timer = None
TIMEZONE = 'Asia/Singapore'

def on_connect(client, userdata, flags, rc):
    print('Connected with result code ' + str(rc))
    client.subscribe('image')
    print('Listening')


def on_message(client, userdata, message):
    global TIMEZONE
    global CVA_THRESHOLD_HI
    global CVA_THRESHOLD_LO
    timerManager('RESET', client)
    Path(IMAGE_FOLDER_PATH).mkdir(parents=True, exist_ok=True)

    print('Message Received')

    existingFiles = glob.glob(IMAGE_FOLDER_PATH + '*')
    for f in existingFiles:
        os.remove(f)

    existingFiles = glob.glob(JSON_FOLDER_PATH + '*')
    for f in existingFiles:
        os.remove(f)

    existingFiles = glob.glob(OUTPUT_FOLDER_PATH + '*')
    for f in existingFiles:
        os.remove(f)

    imgdata = base64.b64decode(message.payload)
    today = IMAGE_FOLDER_PATH + datetime.now(pytz.timezone(TIMEZONE)).strftime('%d-%m-%y_%H-%M-%S')
    filename = today + '.jpg'
    with open(filename, 'wb') as f:
        f.write(imgdata)
        filenameShort = os.path.basename(filename)
        inputName = filenameShort[0:len(filenameShort)-4]
        inputDate = inputName[6:8] + '-' + inputName[3:5] + '-' + inputName[0:2]
        inputTime = inputName[9:11] + ':' + inputName[12:14] + ':' + inputName[15:17]
    
    print('Saved to ' + filename)

    try:
        cva = imageProcessor.getAngle()
        angleList = open('/home/pratyushghosh14/angleList.txt', 'a')
        if(math.isnan(cva)):
                client.publish('posture', 'math_error')
                angleList.close()
                print(colored('published math error', 'red'))
        elif((cva < CVA_THRESHOLD_LO) or (cva > CVA_THRESHOLD_HI)):
                if(cva < CVA_THRESHOLD_LO): postureFlag = 'LO'
                else: postureFlag = 'HI'
                angleList.write(inputDate + ' ' + inputTime + ',' + str(cva) + ',BAD,' + postureFlag + '\n')
                angleList.close()
                currentImage = open(imageProcessor.getCurrentImage(), 'rb')
                encodedPayload = base64.b64encode(currentImage.read() + (' ' + postureFlag).encode('utf-8'))
                client.publish('posture', encodedPayload)
                print(colored('published bad', 'yellow'))
                print('CVA_THRESHOLD_LO: '+str(CVA_THRESHOLD_LO))
                print('CVA_THRESHOLD_HI: '+str(CVA_THRESHOLD_HI))
                print('CVA_DETECTED: '+str(cva))
        else: 
                angleList.write(inputDate + ' ' + inputTime + ',' + str(cva) + ',GOOD,NA\n')
                angleList.close()
                client.publish('posture', 'good_posture')
                print(colored('published good', 'green'))
                print('CVA_THRESHOLD_LO: '+str(CVA_THRESHOLD_LO))
                print('CVA_THRESHOLD_HI: '+str(CVA_THRESHOLD_HI))
                print('CVA_DETECTED: '+str(cva))
    except IndexError:
        client.publish('posture', 'no_human_detected')
        print(colored('published no human detected', 'red'))
    except ValueError:
        client.publish('posture', 'math_error')
        print(colored('published math error', 'red'))

def timerManager(flag, client):
    global timer
    if(flag == 'RESET'):
        timer.cancel()
    timer = threading.Timer(10.0, timeoutMessage, args = [client])
    timer.start()

def timeoutMessage(client):
    client.publish('posture', 'timeout')
    print(colored('published timeout', 'blue'))
    timerManager('CREATE', client)


def setup(hostname):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(username = 'Device4', password = 'Password123')
    client.connect(hostname, 1884, 60)
    timerManager('CREATE', client)
    client.loop_forever()
    return client

def main():
    setup(host_ip)

    while True:
        pass


if __name__ == '__main__':
    main()

