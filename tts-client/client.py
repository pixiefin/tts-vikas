import socketio
import os
import eventlet
import eventlet.wsgi

from flask import Flask, render_template

# Common Vars
TTS_SERVER_URL = 'https://tts-vikas.msriva.com'
LOCAL_SERVER_PORT = 9096
AUDIO_JSON_KEY = 'audio_event'
WORD_JSON_KEY = 'text_event'
TEMPLATE_FILE_NAME = 'index.html'
FLASK_APP_SECERT_KEY = 'SECRET_KEY'
FLASK_APP_SECERT_VAL = '#some_sec_val#'

# File Vars
FILENAME_PREFIX = './'
FILENAME_SUFFIX = '/'
FILE_SAVE_MODE = 'wb'
AUDIO_BASE_FOLDER = 'mp3'
AUDIO_BASE_EXTENSION = '.mp3'
FULL_FILE_PATH = FILENAME_PREFIX + AUDIO_BASE_FOLDER + FILENAME_SUFFIX

# Standard Notifications/Logs
CONN_TO_TTS_SERVER  = 'Local Server Connected to TTS-Server'
DISCONN_FROM_TTS_SERVER  = 'Local Server Disconnected from TTS-Server'
WEB_CLIENT_CONN_TO_LOCAL_SERVER  = 'Local Web Client Connected to Local Server : '
WEB_CLIENT_DISCONN_FROM_LOCAL_SERVER = 'Local Web Client Disonnected from Local Server : '
RCVD_DATA_FROM_TTS_SERVER = 'Local Server Received audio data from TTS-Server the word -->  '
MSG_FWDED_TO_TTS_SERVER = 'Local Server forwarded this Web Client\'s Message to TTS-Server : '
MSG_FROM_LOCAL_WEB_CLIENT = 'Local Server Received Message from this Web Client : '
SAVED_FILED = 'Saved Audio : '

# Events
TTS_SERVER_RCV_EVENT = 'processed_event'
TTS_SERVER_SEND_EVENT = 'text_msg'
LOCAL_SERVER_RCV_EVENT = 'local_msg'
LOCAL_SERVER_SEND_EVENT = 'local_events'

# Socket Client to TTS-SERVER
sio = socketio.Client()

# Socket and Flask Server for Local Web Client -- Add Rooms and Namespace Later
sio_local = socketio.Server()
app = Flask(__name__)
app.wsgi_app = socketio.WSGIApp(sio_local, app.wsgi_app)
# Chnage this later
app.config[FLASK_APP_SECERT_KEY] = FLASK_APP_SECERT_VAL

# Socket Client Event Handlers
@sio.event
def connect():
    print(CONN_TO_TTS_SERVER)
    notifyWebClient(CONN_TO_TTS_SERVER)

@sio.event
def disconnect():
    print(DISCONN_FROM_TTS_SERVER)
    notifyWebClient(DISCONN_FROM_TTS_SERVER)

@sio.on(TTS_SERVER_RCV_EVENT)
def handleDataFromTTSServer(msg):
    word = msg[WORD_JSON_KEY]
    print(RCVD_DATA_FROM_TTS_SERVER + word)
    notifyWebClient(RCVD_DATA_FROM_TTS_SERVER + word)

    #Might not work on Windows to create directory
    filename = FULL_FILE_PATH + word + AUDIO_BASE_EXTENSION
    notifyWebClient(SAVED_FILED + filename)
    with open(filename, FILE_SAVE_MODE) as f:
        f.write(msg[AUDIO_JSON_KEY])

def connect_server():
    sio.connect(TTS_SERVER_URL)

def sendMessageToTTSServer(msg):
    sio.call(TTS_SERVER_SEND_EVENT, msg)


# Socket Server Event Handlers
@app.route('/')
def index():
    return render_template(TEMPLATE_FILE_NAME)

@sio_local.event
def connect(localSocketId, environ):
    print(WEB_CLIENT_CONN_TO_LOCAL_SERVER, localSocketId)

@sio_local.event
def disconnect(localSocketId):
    print(WEB_CLIENT_DISCONN_FROM_LOCAL_SERVER, localSocketId)

@sio_local.on(LOCAL_SERVER_RCV_EVENT)
def handleLocalWebClientMsg(localSocketId, msg):
    print(MSG_FROM_LOCAL_WEB_CLIENT, msg)
    notifyWebClient(MSG_FROM_LOCAL_WEB_CLIENT + msg)

    #Notify the Local Web Client
    notifyWebClient(MSG_FWDED_TO_TTS_SERVER + msg)

    #Forward the Message to TTS-Server
    sendMessageToTTSServer(msg)
    

def notifyWebClient(msg):
    sio_local.emit(LOCAL_SERVER_SEND_EVENT, msg)

if __name__ == '__main__':
    try:
        os.makedirs(AUDIO_BASE_FOLDER)
    except OSError:
        pass
    connect_server()
    eventlet.wsgi.server(eventlet.listen(('', LOCAL_SERVER_PORT)), app)