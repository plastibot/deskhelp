#!/home/pi/citro/bin/python

import os
import json
import serial
import time
from os.path import join, dirname
from dotenv import load_dotenv
from watson_developer_cloud import SpeechToTextV1 as SpeechToText
from watson_developer_cloud import ConversationV1
from watson_developer_cloud import ToneAnalyzerV3
from watson_developer_cloud import TextToSpeechV1

from audio_io.audio_io import AudioIO 
from neopixel import *

# LED strip configuration:
LED_COUNT      = 7      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 64     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
#LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
#LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering

context = {}

def rainbowCycle(strip, wait_ms=20, iterations=5):
  """Draw rainbow that uniformly distributes itself across all pixels."""
  for j in range(256*iterations):
    for i in range(strip.numPixels()):
      strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
    strip.show()
    time.sleep(wait_ms/1000.0)

    
def theaterChaseRainbow(strip, wait_ms=50):
  """Rainbow movie theater light style chaser animation."""
  for j in range(256):
    for q in range(3):
      for i in range(0, strip.numPixels(), 3):
	strip.setPixelColor(i+q, wheel((i+j) % 255))
      strip.show()
      time.sleep(wait_ms/1000.0)
      for i in range(0, strip.numPixels(), 3):
	strip.setPixelColor(i+q, 0)


def transcribe_audio(stt, path_to_audio_file):
  with open(join(dirname(__file__), path_to_audio_file), 'rb') as audio_file:
    return stt.recognize(audio_file,
      content_type='audio/wav')


def main():
  try:
    ser = serial.Serial('/dev/serial0', 9600, timeout=1)
    ser.isOpen()
    print ("port is opened")
  except IOError:
    ser.close()
    ser.open()
    print("port was already open, was closed and opene again")


  dotenv_path = join(dirname(__file__), '.env')
  load_dotenv(dotenv_path)
  
  stt = SpeechToText(
          username=os.environ.get("STT_USERNAME"),
          password=os.environ.get("STT_PASSWORD"))

  workspace_id = os.environ.get("WORKSPACE_ID")
  conversation = ConversationV1(
      username=os.environ.get("CONVERSATION_USERNAME"),
      password=os.environ.get("CONVERSATION_PASSWORD"),
      version='2016-09-20')

  tone_analyzer = ToneAnalyzerV3(
      username=os.environ.get("TONE_ANALYZER_USERNAME"),
      password=os.environ.get("TONE_ANALYZER_PASSWORD"),
      version='2016-02-11')

  tts = TextToSpeechV1(
    username=os.environ.get("TTS_USERNAME"),
    password=os.environ.get("TTS_PASSWORD"),
    x_watson_learning_opt_out=True)  # Optional flag

  # Create NeoPixel object with appropriate configuration.
  strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
  # Intialize the library (must be called once before other functions).
  strip.begin()
  
  current_action = ''
  msg_out = ''

  while current_action != 'end_conversation':
    message = listen(stt)
#    emotion = get_emotion(tone_analyzer, message)
    print(message)
    response = send_message(conversation, workspace_id, message, "sad") 

    # Check for a text response from API
    if response['output']['text']:
      msg_out = response['output']['text'][0]

    # Check for action flags sent  by the dialog
    if 'action' in response['output']:
      current_action = response['output']['action']

    # User asked what time is it, so we output the local system time
    if current_action == 'display_time':
      msg_out = 'The current time is ' + time.strftime('%I:%M %p')
      current_action = ''

    # User asked bot to turn red
    if current_action == 'red':
      msg_out = 'Turning Red'
      for pix in range(0, strip.numPixels()):
        strip.setPixelColor(pix, Color(255, 0, 0))
        strip.show()
        time.sleep(50/1000.0)
      current_action = ''

    # User asked bot to turn green
    if current_action == 'green':
      msg_out = 'Turning green'
      for pix in range(0, strip.numPixels()):
        strip.setPixelColor(pix, Color(0, 255, 0))
        strip.show()
        time.sleep(50/1000.0)
      current_action = ''
      
    # User asked bot to turn blue
    if current_action == 'blue':
      msg_out = 'Turning blue'
      for pix in range(0, strip.numPixels()):
        strip.setPixelColor(pix, Color(0, 0, 255))
        strip.show()
        time.sleep(50/1000.0)
      current_action = ''

    # User asked bot to turn disco
    if current_action == 'disco':
      msg_out = 'Turning disco'
      theaterChaseRainbow(strip)
      current_action = ''

    # User asked bot to set rainbow color
    if current_action == 'raibow':
      msg_out = 'Turning rainbow'
      RainbowCycle(strip)
      current_action = ''

      
    print(msg_out)

    speak(tts, msg_out)
    #recorder.play_from_file("output.wav")

  ser.close()
    

def listen(stt):
  recorder = AudioIO("input.wav")

  print("Please say something into the microphone\n")
  recorder.record_to_file()

  print("Transcribing audio....\n")
  result = transcribe_audio(stt, 'input.wav')

  print(result)

  try:
    text = result['results'][0]['alternatives'][0]['transcript']
  except IndexError:
    text = "I didn't get it"
  print("Text: " + text + "\n")
  return text  


def get_emotion(tone_analyzer, text):
  result = tone_analyzer.tone(text=text)
  tones = result['document_tone']['tone_categories'][0]['tones']

  max_score = 0
  max_emotion = ''
  for tone in tones:
    if float(tone['score']) > max_score:
      max_emotion = tone['tone_id']
      max_score = float(tone['score'])

  return max_emotion


def send_message(conversation, workspace_id, message, emotion):
  global context
  context['emotion'] = emotion

  response = conversation.message(
    workspace_id=workspace_id,
    input={'text': message},
    context=context)

  if response['output']['text']:
    print(response['output']['text'][0])

  print(json.dumps(response, indent=4))
  
  context = response['context']

  return response

def speak(tts, text):
  with open('output.wav', 'wb') as audio_file:
    audio_file.write(
      tts.synthesize(
        text, 
        accept="audio/wav",
        voice="en-US_AllisonVoice"))

  player = AudioIO("output.wav")

  #print("Please say something into the microphone\n")
  player.play_from_file("output.wav")

  
  
if __name__ == '__main__':
  try:
    main()
  except:
    print("IOError detected, restarting...")
    main()



