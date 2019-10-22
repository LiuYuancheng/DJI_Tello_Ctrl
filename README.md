# DJI_Tello_Ctrl

#### Introduction

This project will create DJI Tello Drone controller program. It also use the ESP8266 Arduino to read the data from HC-SR04 Ultrasonic Sensor to do the the fly environment monitoring function. It also provide the sensor firmware attestation function by using the "PATT" algorithm.  

###### Program Main UI View: 

![](https://github.com/LiuYuancheng/DJI_Tello_Ctrl/blob/master/doc/2019-10-18_123002.jpg)

###### Hardware View:

![](https://github.com/LiuYuancheng/DJI_Tello_Ctrl/blob/master/doc/sernsors.JPG)

------

###### Development env: Python 3.7

###### Additional Lib need: 

1. wxPython 4.0.6 (build UI this lib need to be installed) 

[wxPython]: https://wxpython.org/pages/downloads/index.html:	"wxPython"

```
pip install -U wxPython 
```

2. OpenCV: opencv-python 4.1.1.26  (need to install to do the H264 video stream decode)

[openCV on Wheel]: https://pypi.org/project/opencv-python/:	"OpenCV"

```
pip install opencv-python
```

###### Hardware Need:

![](https://github.com/LiuYuancheng/DJI_Tello_Ctrl/blob/master/doc/item.jpg)

[DJI Tello ]: https://www.ryzerobotics.com/tello/downloads	"DJI tello control SDK"
[ESP8266 Arduino ]: https://arduino-esp8266.readthedocs.io/en/latest/	"ESP8266 Arduino dev doc"
[HC-SR04 Ultrasonic Sensor ]: https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf	"DJI tello control SDK"

------

#### System Design

###### Communication

| The program will connect to the Arduino by TCP and communicate with the drone by UDP: |
| ------------------------------------------------------------ |
| Arduino  control:  Arduino_192.168.1.101_TCP_PORT:4000<<- ->>  PC_192.168.1.100_TCP_PORT:4000 |
| Send Command & Receive Response:  Tello IP: 192.168.10.1  UDP PORT:8889  <<- ->>  PC/Mac/Mobile |
| Receive Tello State: Tello IP: 192.168.10.1  ->>  PC/Mac/Mobile UDP Server: 0.0.0.0 UDP PORT:8890 |
| Receive Tello Video Stream:  Tello IP: 192.168.10.1  ->>  PC/Mac/Mobile UDP Server: 0.0.0.0 UDP PORT:11111 |

![](https://github.com/LiuYuancheng/DJI_Tello_Ctrl/blob/master/doc/port.png)

###### Connection: 

The Tello drone is connect the computer by WIFI. The Arduino will connect to a router first then connect to the computer.

![](https://github.com/LiuYuancheng/DJI_Tello_Ctrl/blob/master/doc/communicate.png)

###### Program Executions Diagram: 

The main thread will start 3 sub-Thread to communicate with the Arduino, read the tello states data and get the tello Video stream. The main thread will handle the tello control.

![](https://github.com/LiuYuancheng/DJI_Tello_Ctrl/blob/master/doc/workflow.png)

------

#### Program Usage: 

Follow the section "Connection" to connect to the sensor and drone to your computer. 

###### Program execution cmd: 

```
python telloRun.py
```

###### The main Main UI will show:

![](https://github.com/LiuYuancheng/DJI_Tello_Ctrl/blob/master/doc/mainUI.png)

1. Click the "UAV Connect" button under the title line, if the done response correctly the drone state will change to green.  
2. The sensor will connect to the program automatically, When the ESP8266 Arduino connect to the program, the sensor indicator will change to green. 
3. Press the white 'Camera' button under "Takeoff and Cam Ctrl" will turn on the drone's front camera.
4. The latest battery reading will be shown on the left-top corner of the Camera view panel and the height of the drone will be shown on the right side of the the lowest skyline horizontal indicator. The battery reading show in the title bar is the average reading in the passed 10 seconds. 
5.  Track control: 
   - Add a track: Open the track record file "TrackPath.txt"  and add the track by below format: TrackName ;action 1;action x;action x;action x;action x;action x;land (example:Track1;takeoff;command;up 30;ccw 30;up 30;ccw 30;up 30;land ) 
   - Select the track by the drop down menu and click the "Active track" button, the selected track will by executed by the drone. The current executed action will be marked as green colour. 

6. Sensor Firmware attestation control:  

   - fill the how many times of the  attestation you want to do and the memory block size then press the startPatt button. The local firmware and the sensor firmware will be shown and compared. The attestation result and time used will be shown as below (The attestation process will take about 8sec ~ 10 sec): 

   - ![](https://github.com/LiuYuancheng/DJI_Tello_Ctrl/blob/master/doc/attestFail.jpg)

   - Every attestation result will be record in the "checkSumRecord.txt" (source folder) under format: 

     checksum record [2019-10-18 12:18:30.305437]:

     Local:1400A0C126221302030000340C21865C1014050020C0313FBEE0CD0C0B073110FF0C02C174033F4010101C910C38FF7EFFEE0D210D012921020CE00E020012F0

     Remote:1400A0C126221302030000340C21865C1014050020C0313FBEE0CD0C0B073110FF0C02C174033F4010101C910C38FF7EFFEE0D210D012921020CE00E020012F0

     

7. Press the '>>' button the drone detail status information display window will pop-up on the right as shown below: 

------

