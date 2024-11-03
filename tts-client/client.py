import socketio
import os

sio = socketio.Client()

@sio.event
def connect():
    print('Connected to server')

@sio.event
def disconnect():
    print('Disconnected from server')

@sio.on('processed_event')
def handleProcessedEvent(msg):
    print('Saving audio ..')
    filename = './mp3/' + msg['text_event'] + '.mp3'
    print(filename)
    with open(filename, 'wb') as f:
        f.write(msg['audio_event'])

def connect_server():
    sio.connect('https://tts-vikas.msriva.com')

def send_msg(msg):
    sio.call('text_msg', msg)

if __name__ == '__main__':
    try:
        os.makedirs('mp3')
    except OSError:
        pass
    connect_server()

    while (True):
        msg = input("Enter Text --> ")
        send_msg(msg)