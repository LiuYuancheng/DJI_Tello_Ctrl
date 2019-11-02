# DJI_Tello_Ctrl

#### Introduction

This project will create a DJI Tello Drone controller program with the drone basic motion control and track edit function. It will also use the ESP8266 Arduino to read the data from HC-SR04 Ultrasonic Sensor to do the fly environment monitoring function and provide the sensor firmware attestation function by using the "PATT" algorithm.  

###### Program Main UI View: 

![](https://github.com/LiuYuancheng/DJI_Tello_Ctrl/blob/master/doc/2019-10-18_123002.jpg)

###### Hardware View (Done with sensors):

![](https://github.com/LiuYuancheng/DJI_Tello_Ctrl/blob/master/doc/sernsors.JPG)

------

###### Development Env: Python 3.7.4

###### Additional Lib Need: 

1. wxPython 4.0.6 (need to install for UI building) 

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

We use DJI Tello Drone, ESP8266 Arduino and HC-SR04 Ultrasonic Sensor to build the system: 

![](https://github.com/LiuYuancheng/DJI_Tello_Ctrl/blob/master/doc/item.jpg)

[DJI Tello ]: https://www.ryzerobotics.com/tello/downloads	"DJI tello control SDK"
[ESP8266 Arduino ]: https://arduino-esp8266.readthedocs.io/en/latest/	"ESP8266 Arduino dev doc"
[HC-SR04 Ultrasonic Sensor ]: https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf	"DJI tello control SDK"

------

#### System Design

###### Communication Protocol 

| The program will connect to the Arduino by TCP and communicate with the drone by UDP: |
| ------------------------------------------------------------ |
| Arduino  Control:  Arduino_IP: 192.168.1.101, TCP_PORT: 4000 <<- ->>  PC_IP: 192.168.1.100 TCP_PORT: 4000 |
| Drone Control (Send Command & Receive Response):  Tello_IP: 192.168.10.1  UDP_PORT:8889  <<- ->>  PC/Mac/Mobile_IP: 192.168.10.xx UDP_PORT:8889 |
| Drone Control (Receive Tello State): Tello_IP: 192.168.10.1  UDP_PORT:8890 ->>  PC/Mac/Mobile_ UDP_Server: 0.0.0.0, UDP PORT:8890 |
| Drone Control (Receive Tello Video Stream) :  Tello_IP: 192.168.10.1, UDP_PORT:11111->>  PC/Mac/Mobile_UDP_Server: 0.0.0.0,  UDP_PORT:11111 |

![](https://github.com/LiuYuancheng/DJI_Tello_Ctrl/blob/master/doc/port.png)

###### WIFI Connection Diagram: 

The Tello drone will connect the computer by WIFI. The Arduino will connect to a router first then connect to the computer. The connection diagram is shown below: 

![](https://github.com/LiuYuancheng/DJI_Tello_Ctrl/blob/master/doc/communicate.png)

###### Program Executions Diagram: 

The main thread will start 3 sub-Thread to communicate with the Arduino, read the tello states data and get the tello Video stream. The main thread will handle the tello control. Program execution UML diagram: 

![](https://github.com/LiuYuancheng/DJI_Tello_Ctrl/blob/master/doc/workflow.png)

------

#### Program Usage: 

Follow the section "WIFI Connection Diagram" to connect to the sensor and drone to your computer. Then execute the program telloRun.py under src folder by the below command: 

```
python telloRun.py
```

After the init finish show in your terminal: 

```
"Program init finished."
```

 Then the main UI will show as below: 

![](https://github.com/LiuYuancheng/DJI_Tello_Ctrl/blob/master/doc/mainUI.png)

###### Your can follow below steps to control the drone, sensor and do the firmware attestation: 

1. Click the "**UAV Connect**" button under the title line, if the done response correctly the drone state will change to green and the indicator will show "UAV_Online".

2. The sensor will connect to the program automatically. When the ESP8266 Arduino connected to the program, the sensor indicator will change to green and show "SEN_Online". 

3. Press the white 'Camera' button under "Takeoff and Cam Ctrl" will turn on the drone's front camera.

4. The latest battery reading will be shown on the left-top corner of the front camera view panel and the height of the drone will be shown on the right side of the the lowest skyline horizontal indicator. The battery reading show in the title bar is the average reading in the passed 10 seconds. 

5. Drone track path planning: 
   - Add a track: Open the track record file "TrackPath.txt"(under src folder)  and add the track by below format: TrackName**;**action 1**;**action x**;**action x**;**action x**;**action x**;**action x**;**land (example:*Track1;takeoff;command;up 30;ccw 30;up 30;ccw 30;up 30;land* . If you don't set the land cmd the program will add the land cmd automatically. For the action please check the detail drone control protocol in Tello SDK Documentation EN_1.3_1122.pdf under doc folder ) 
   - Select the track by the drop down menu and click the "Active track" button, the selected track will by executed by the drone. The current executed action will be marked as green colour. 

6. Sensor Firmware Attestation Control:  

   - Fill attestation times you want to do and the memory block size, then press the "startPatt" button. The local firmware and the sensor firmware will be shown and compared. The attestation result and total time used for the attestation process will be shown as below (The attestation process will take about 8sec ~ 10 sec): 

   - ![](https://github.com/LiuYuancheng/DJI_Tello_Ctrl/blob/master/doc/attestFail.jpg)

   - Every attestation result will be record in the "checkSumRecord.txt" (source folder) under format: 

     checksum record [2019-10-18 12:18:30.305437]:

     Local:1400A0C126221302030000340C21865C1014050020C0313FBEE0CD0C0B073110FF0C02C174033F4010101C910C38FF7EFFEE0D210D012921020CE00E020012F0

     Remote:1400A0C126221302030000340C21865C1014050020C0313FBEE0CD0C0B073110FF0C02C174033F4010101C910C38FF7EFFEE0D210D012921020CE00E020012F0

     

7. Press the '>>' button under the title bar the drone detail status information display window will pop-up on the right.

------

