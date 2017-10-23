import os
import json
from os.path import join, dirname
from dotenv import load_dotenv
from watson_developer_cloud import SpeechToTextV1 as SpeechToText
from watson_developer_cloud import ConversationV1
from watson_developer_cloud import ToneAnalyzerV3
from watson_developer_cloud import TextToSpeechV1

from audio_io.audio_io import AudioIO 


context = {}

def transcribe_audio(stt, path_to_audio_file):
  with open(join(dirname(__file__), path_to_audio_file), 'rb') as audio_file:
    return stt.recognize(audio_file,
      content_type='audio/wav')


def main():
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


  while(True):
    message = listen(stt)
    emotion = get_emotion(tone_analyzer, message)
    response = send_message(conversation, workspace_id, message, emotion) 
    speak(tts, response['output']['text'][0])
    #recorder.play_from_file("output.wav")

    

def listen(stt):
  recorder = AudioIO("input.wav")

  print("Please say something into the microphone\n")
  recorder.record_to_file()

  print("Transcribing audio....\n")
  result = transcribe_audio(stt, 'input.wav')
  
  text = result['results'][0]['alternatives'][0]['transcript']
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
    message_input={'text': message},
    context=context)
  context = response['context']

  print(response['output']['text'][0])
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



