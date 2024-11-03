import socketio
import eventlet
import eventlet.wsgi
import time
from gtts import gTTS
from io import BytesIO

sio = socketio.Server()
app = socketio.WSGIApp(sio)

@sio.event
def connect(sid, environ):
    print('Client connected: ', sid)

@sio.event
def disconnect(sid):
    print('Client disconnected:', sid)

@sio.on('text_msg')
def handleMsg(sid, msg):
    print('Text Message : ', msg)
    processMessage(msg)

def convertToSpeech(msg):
    print("Converting Text : ", msg)

    audio_byte_stream = BytesIO()

    tts = gTTS(msg, lang='en')
    tts.write_to_fp(audio_byte_stream)
    audio_byte_stream.seek(0)
    return audio_byte_stream.getvalue()

def handleWord(word, process=True):
    speech = convertToSpeech(word)
    response = {
        'audio_event' : speech,
        'text_event':  word
    }
    sio.emit('processed_event', response)
    
def processMessage(msg):
    tokenized = msg.split()
    if len(tokenized) == 1 :
        handleWord(tokenized[0])
    else :
        for word in tokenized:
            handleWord(word)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 9069)), app)