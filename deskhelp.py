import snowboydecoder
import sys
import signal
#import speech_recognition as sr
import os
import json
import time
import wave
import pyaudio
from os.path import join, dirname
from dotenv import load_dotenv
from watson_developer_cloud import SpeechToTextV1 as SpeechToText
from watson_developer_cloud import ConversationV1
from watson_developer_cloud import TextToSpeechV1

#from audio_io.audio_io import

interrupted = False
context = {}
current_action = ''

def transcribe_audio(stt, path_to_audio_file):
    with open(join(dirname(__file__), path_to_audio_file), 'rb') as audio_file:
        return stt.recognize(audio_file, content_type='audio/wav')

def send_message(conversation, workspace_id, message):
    global context
    response = conversation.message(
        workspace_id=workspace_id,
        input={'text': message},
        context=context)

    context = response['context']
    return response


def speak(tts, text):
    with open('output.wav', 'wb') as audio_file:
        audio_file.write(
            tts.synthesize(
                text,
                accept="audio/wav",
                voice="en-US_AllisonVoice"))

    #snowboydecoder.play_audio_file('output.wav')

    wf = wave.open('output.wav', 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(), rate=wf.getframerate(),
                    output=True)

    data = wf.readframes(1024)

    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(1024)

    stream.stop_stream()
    stream.close()

    p.terminate


    
def audioRecorderCallback(fname):
    print("converting audio to text")
    current_action = ''

#    result = transcribe_audio(stt, fname)
    
    try:
        result = transcribe_audio(stt, fname)
    except UnknownValueError:
        print("IBM Watson Speech Recognition could not understand audio")
    except RequestError as e:
        print("Could not request results from IBM Watson Speech Recognition service; {0}".format(e))

    try:
        text = result['results'][0]['alternatives'][0]['transcript']
    except IndexError:
        text = "sorry, I didn't get that, please say it again"
    print('Text: ' + text + '\n')

    response = send_message(conversation, workspace_id, text)

    # Check for a text response from Conversation API
    if response['output']['text']:
        msg_out = response['output']['text'][0]

    # Check for action fags sent from Conversation API
    if 'action' in response['output']:
        current_action = response['output']['action']

    # Testing for different actions

    # User asked for the time?
    if current_action == 'display_time':
        msg_out='The current time is ' + time.strftime('%I:%M:%S %p')
        current_action = ''
    
    print(msg_out)

    speak(tts, msg_out)
    
    os.remove(fname)



def detectedCallback():
    snowboydecoder.play_audio_file()
    print('recording audio...', end='', flush=True)

def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

model = os.environ.get("SNOWBOY_MODEL")

stt = SpeechToText(
    username = os.environ.get("STT_USERNAME"),
    password = os.environ.get("STT_PASSWORD"))

workspace_id = os.environ.get("WORKSPACE_ID")

conversation = ConversationV1(
    username = os.environ.get("CONVERSATION_USERNAME"),
    password = os.environ.get("CONVERSATION_PASSWORD"),
    version='2016-02-11')

tts = TextToSpeechV1(
    username=os.environ.get("TTS_USERNAME"),
    password=os.environ.get("TTS_PASSWORD"),
    x_watson_learning_opt_out=True) # Optional flag

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
print('Listening... Press Ctrl+C to exit')

# main loop
current_action=''
detector.start(detected_callback=detectedCallback,
               audio_recorder_callback=audioRecorderCallback,
               interrupt_check=interrupt_callback,
               sleep_time=0.01)

detector.terminate()


