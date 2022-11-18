import paho.mqtt.client as mqtt

host_ip = '34.81.217.13'  # Broker IP

def on_connect(client, userdata, flags, rc):
    print('Connected with result code ' + str(rc))
    client.publish('message/Activity','Sit Stand Too Long')
    print('Signaled')
    #quit()


def on_message(client, userdata, message):
    return 0

def setup(hostname):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(username = 'Device7', password = 'Password123')
    client.connect(hostname, 1884, 60)
    client.loop_forever()
    return client

def main():
    setup(host_ip)

    while True:
        pass

if __name__ == '__main__':
    main()
