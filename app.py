import serial
from flask import Flask, render_template, request
app = Flask(__name__)

try:
    ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
    ser.isOpen()
    print ("port is opened")

except IOError:
    ser.close()
    ser.open()
    print("port was already open, was closed and opened again")


@app.route("/")
def main():
   # Pass the template data into the template main.html and return it to the user
   templateData = {
   'voltage' : 420
   }

   return render_template('main.html', **templateData)

# The function below is executed when someone requests a URL with the mode and action in it:
# mode can be: 1=PROG_MEM or 2=PROG_MEM_STATE
@app.route("/<mode>/<action>")
def action(mode, action):
   # Convert the mode from the URL into an integer
   # mode = int(mode)
   # Convert the action from the URL into an integer
   # action = int(action)
   # Compose your serial message here to send to ESP8266
   # ser.write("1,7=")
   test_string = "1,7="
   msg = mode+','+action+'='
   ser.write(msg.encode())
   # collect new value for voltage here from serial input 


   # Pass the template data into the template main.html and return it to the user
   templateData = {
   'voltage' : 420
   }
   
   return render_template('main.html', **templateData)

   

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, debug=True)
