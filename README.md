# Lost and Found

Prototype for the Schaeffler challenge built on [HACK|BAY](https://www.hackbay.de) 2024.

Team Members:
- Julia Kornatzki
- Waseem Randhawa
- Prathik Prasad
- Linus See
- Naveen Narasimhappa

## Tracking Backend
Run `npm install` to install all dependencies. 

To start the local server navigate to `/tracking-backend` and run `npm run start`

## QR Code Detection
Run `source PATH_TO_FOLDER/lost-and-found/venv/bin/activate pip install opencv-python|requests|pyserial|playsound|qreader` for every dependency to install them.
On Mac and Linux systems you may need to install the library `zbar` as well. 


Before starting the detection app you should check the settings in `qr-code-detection.py`

Turn `use_led_lights` off when you do not have a LED light connected to your computer.
If you do have LED lights, check the port and baud rate of the serial connection. You may have to adjust both. 

Turn `use_camera` off when you want to process one of the given videos in `/qr-code-detection/videos` instead of using your camera.


When everything is set, run `PATH_TO_FOLDER/lost-and-found/venv/bin/python PATH_TO_FOLDER/lost-and-found/qr-code-detection.py` to start the application. 