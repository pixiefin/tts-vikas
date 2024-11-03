import socketio
import os

sio = socketio.Client()

@sio.event
def connect():
    print('Connected to server')

@sio.event
def disconnect():
    print('Disconnected from server')

@sio.event
def srv_ack(data):
    print('Message from server: ', data)

@sio.on('text_event')
def handleWord(msg):
    print('Text Message : ', msg)

@sio.on('audio_event')
def handleAudio(msg):
    print('Saving audio ..')

@sio.on('processed_event')
def handleProcessedEvent(msg):
    print('Saving audio ..')
    filename = './mp3/' + msg['text_event'] + '.mp3'
    print(filename)
    with open(filename, 'wb') as f:
        f.write(msg['audio_event'])

def connect_server():
    sio.connect('https://tts-vikas.msriva.com')

def send_msg():
    sio.emit('text_msg', 'This is a test')

if __name__ == '__main__':
    try:
        os.makedirs('mp3')
    except OSError:
        pass

    connect_server()
    send_msg()
    sio.wait()