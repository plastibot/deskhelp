# pybot

Brains for my Biped Robot. See repo "citro.git" for Robot assembly instructions.

Runs on Raspbian on a Raspberry Pi Zero W. Pybot uses python 3.6 and communicates using PySerial to an ESP8266 controlling all the RC Servo movements.

Uses Watson for voice and video capabilities.


## INSTALLATION

Start with a fresh Raspbian image from https://www.raspberrypi.org/downloads/raspbian/

### Set your USB Audio device as default

To find what address your device uses you need to first enter the command aplay -l this shows all audio output devices, and their address. For example, my USB sound card comes up as device 1 in the output which looks like this.

```
$ aplay -l
card 0: ALSA [bcm2835 ALSA], device 0: bcm2835 ALSA [bcm2835 ALSA]
Subdevices: 8/8
Subdevice #0: subdevice #0
Subdevice #1: subdevice #1
Subdevice #2: subdevice #2
Subdevice #3: subdevice #3
Subdevice #4: subdevice #4
Subdevice #5: subdevice #5
Subdevice #6: subdevice #6
Subdevice #7: subdevice #7
card 1: Device [USB PnP Sound Device], device 0: USB Audio [USB Audio]
Subdevices: 0/1
Subdevice #0: subdevice #0
```

Now, to set the device to your default card you will need to edit the file /usr/share/alsa/alsa.conf with the command sudo nano /usr/share/alsa/alsa.conf scroll down until you find the lines

```
defaults.ctl.card 0
defaults.pcm.card 0
```

and change them to (if your device is also listed as device 1, if not change the 1 to whatever address it was listed at)

```
defaults.ctl.card 1
defaults.pcm.card 1
```

Create and edit the file ~/.asoundrc by using the command sudo nano ~/.asoundrc and change it so that it only reads this:

```
pcm.!default {
  type plug
  slave {
    pcm "hw:1,0”
  }
}

ctl.!default {
  type hw
  card 1
}
```

Now your default audio out (speakers) and audio in (mic) are your usb device.
You can verify by runing the following and hearing sound on your speaker
aplay /usr/share/sounds/alsa/Front_Center.wav
and running the following ocmmand and being able to record your voice
arecord test.wav



### Install latest version of Python 3.6.x

Installing dependencies:
```
$ sudo apt-get -y install libbz2-dev liblzma-dev libsqlite3-dev libncurses5-dev libgdbm-dev zlib1g-dev libreadline-dev libssl-dev tk-dev build-essential libncursesw5-dev libc6-dev openssl
```

Downloading needful version (execution time depends of channel bandwidth):
```
$ cd ~
$ wget https://www.python.org/ftp/python/3.6.0/Python-3.6.0.tgz
$ tar -zxvf Python-3.6.0.tgz
```

Configure, build and install from source:
```
$ cd Python-3.6.0
$ ./configure
$ make
$ sudo make install
```

Create and activate your virtual enviroment
```
$ python3 -m venv citro
$ source ~/citro/bin/activate
```

### install Python libraries

Watson-Devloper-Cloud
```
pip install —upgrade watson-developer-cloud
```

*** If it fails installin ffi you will need to install libffi using sudo apt-get install libffi-dev

install python-dotenv
```
pip install python-dotenv
```

install Portaudio and PyAudio
```
sudo apt-get install portaudio19-dev
pip install pyaudio
```
