# DeskHelp

A Desk assistant controlled by voice commands. 

Runs on Raspbian on a Raspberry Pi Zero W. Programmed using python 3.6. Uses the IBM Watson API for voice capabilities. Uses the GPIO to control neopixels to let other people know your status (i.e Green color - available to talk, Red color - unavailable, Blue color - Out of the office, etc.)


## INSTALLATION

Start with a fresh Raspbian image from https://www.raspberrypi.org/downloads/raspbian/

1. Transfer the Raspbian image to your SD card. https://www.raspberrypi.org/learning/software-guide/quickstart/

2. Insert Sd card, Connect a keyboard and Monitor to your Raspberry Pi Zero W. https://www.raspberrypi.org/learning/hardware-guide/quickstart/

3. Connect to wireless. https://www.raspberrypi.org/learning/software-guide/wifi/

4. Run Raspi-config and enable SSH and VNC. https://www.raspberrypi.org/learning/teachers-guide/remote/

5. configure Locals for Keyboard, Languaje, time and wifi.


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

Now your default audio out (speakers) and audio in (mic) are your usb device. You can verify by runing the following command and recording sound on your microphone

```
$ arecord  t.wav
```

press Control+C on your keyboard to stop recording, and then use the following command to play the sound you just recorded on your speakers.

```
$ aplay t.wav
```

### Install latest version of Python 3.6.x

At the time of this tutorial the latest version of Python was 3.6.4. The instructions below are for that version. If you want the latest version, simply replace the version number accordingly on the commands below.

Installing dependencies:
```
$ sudo apt-get -y install libbz2-dev liblzma-dev libsqlite3-dev libncurses5-dev libgdbm-dev zlib1g-dev libreadline-dev libssl-dev tk-dev build-essential libncursesw5-dev libc6-dev openssl
```

Download Python:
```
$ cd ~
$ wget https://www.python.org/ftp/python/3.6.4/Python-3.6.4.tgz
$ tar -zxvf Python-3.6.4.tgz
```

Configure, build and install from source:
```
$ cd Python-3.6.4
$ ./configure
$ make
$ sudo make install
```

### install Python libraries

Watson-Devloper-Cloud
```
sudo apt-get install libffi-dev
sudo pip3 install —upgrade watson-developer-cloud
```

install python-dotenv
```
sudo pip3 install python-dotenv
```

install Portaudio and PyAudio
```
sudo apt-get install portaudio19-dev
sudo pip3 install pyaudio
```

install NeoPixel library fo rLED control
```
sudo pip3 install rpi_ws281x
```
