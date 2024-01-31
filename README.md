# DJI_Tello_Control [Drone Firmware attack and detection]

**Program Design Purpose**: The objective of this cyber attack case study is to develop a workshop which use the terrain matching drone program and the firmware attestation algorithm introduced in paper [PAtt: Physics-based Attestation of Control Systems](https://www.usenix.org/system/files/raid2019-ghaeini.pdf)  for demonstrating the IoT/OT device firmware attack and the attack detection. The terrain matching drone is build by four distance sensors and DJI Tello Drone.

**Attacker Vector** : Malicious Firmware Updates (OT), IoT Supply Chain Attacks

> Important : The demonstrated attack case is used for education and training for different level of IT-OT cyber security ICS course, please don't apply it on any real world system.

[TOC]

------

### Introduction

This project contains two sections: 

- DJI Tello Terrain Matching Drone Control 
- 

##### **DJI Tello Terrain Matching Drone Control** 

In this project we add four additional distance detection sensor under a DJI Tello drone, then we use the Tello's bottom sensor and the 4 distance sensor to generate the drone bottom ground contour map, then our main drone controller will control the drone based on the contour map. For example, if we want the drone fly straight until detect a table sharp item under it, the drone will keep send the contour map to control program and if the program detect that the can match pre-saved table's feature, the control program will send the landing command to the drone.

![](doc/img/terrain_match.png)









In this section we will create a DJI Tello Drone controller program with the drone basic motion control, track editing function and drone motion safety check function. 







##### **Arduino Firmware Attestation**

In this section we will create a firmware program running on the ESP8266 Arduino to read the distances data from HC-SR04 Ultrasonic Sensor to do the fly environment monitoring, terrain matching function and provide the sensor firmware attestation function by using the "PATT"(PAtt: Physics-based Attestation of Control Systems) algorithm to confirm the firmware is not changed by attacker.  

**Demo Link**: 

https://www.youtube.com/watch?v=rRu1qrZohJY

```
[![Demo video](https://yt-embed.herokuapp.com/embed?v=rRu1qrZohJY)](https://www.youtube.com/watch?v=rRu1qrZohJY "Demo video ")
```

##### Program Main UI View

The main user interface to control the drone and check the sensor state is shown below:

![](doc/img/2019-10-18_123002.jpg)

##### Hardware View (Done with sensors installed)

The Two sensors doing terrain matching are mounted under the drone as shown below:

![](doc/img/sernsors.JPG)

`version: v_0.2`



------

### Program Setup

###### Development Environment

> Python 3.7.4, C

###### Additional Lib Need

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

###### Hardware Need

We use DJI Tello Drone, ESP8266 Arduino and HC-SR04 Ultrasonic Sensor to build the system: 

![](doc/img/item.jpg)

[DJI Tello ]: https://www.ryzerobotics.com/tello/downloads	"DJI tello control SDK"
[ESP8266 Arduino ]: https://arduino-esp8266.readthedocs.io/en/latest/	"ESP8266 Arduino dev doc"
[HC-SR04 Ultrasonic Sensor ]: https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf	"DJI tello control SDK"



------

### System Design

##### Communication Protocol 

The control hub (Computer) will control with the drone by UDP and fetch the feedback data of the sensor by TCP:

| The program will connect to the Arduino by TCP and communicate with the drone by UDP |
| ------------------------------------------------------------ |
| **Arduino  Control**:  Arduino_IP: 192.168.1.101, TCP_PORT: 4000 <<- ->>  PC_IP: 192.168.1.100 TCP_PORT: 4000 |
| **Drone Control** (Send Command & Receive Response):  Tello_IP: 192.168.10.1  UDP_PORT:8889  <<- ->>  PC/Mac/Mobile_IP: 192.168.10.xx UDP_PORT:8889 |
| **Drone Control** (Receive Tello State): Tello_IP: 192.168.10.1  UDP_PORT:8890 ->>  PC/Mac/Mobile_ UDP_Server: 0.0.0.0, UDP PORT:8890 |
| Drone Control (Receive Tello Video Stream) :  Tello_IP: 192.168.10.1, UDP_PORT:11111->>  PC/Mac/Mobile_UDP_Server: 0.0.0.0,  UDP_PORT:11111 |

**Communication detail diagram is shown below**: 

![](doc/img/port.png)

###### WI-FI Connection Diagram

The Tello drone will connect the computer by WI-FI. The Arduino will connect to a router first then connect to the computer. The connection diagram is shown below: 

![](doc/img/communicate.png)

###### Program Executions Diagram

The main thread will start three parallel sub-thread to communicate with the Arduino, read the Tello states data and get the Tello's UDP Video stream. The main thread will handle the Tello control. Program execution UML diagram: 

![](doc/img/workflow.png)

##### Program File List 

| Program File          | Execution Env | Description                                                  |
| --------------------- | ------------- | ------------------------------------------------------------ |
| esp_client.ino        | C(Arduino)    | This module will start a TCP client to send the HC-SR04 Ultrasonic Sensor reading to server and send the firmware checksum for attestation. |
| esp_client_attack.ino | C(Arduino)    | Attack firmware: It has the same function as the file <esp_client.ino>, but if we compile this program and load the firmware in to the Arduino, the sensor feed back will be set to a fixed number. |
| telloGlobal.py        | python3.7.4   | This module is used as a Local config file to set constants and global parameters which will be used in the other modules. |
| TelloPanel.py         | python 3.7    | This module is used to create the control and display panel for the UAV system (drone control and sensor firmware attestation). |
| TelloRun.py           | python 3.7    | This module is used to create a controller for the DJI Tello Drone and connect to the Arduino_ESP8266 to get the height sensor data. |
| telloSensor.py        | python 3.7    | This module is used to create a TCPcommunication server to receive the Arduino_ESP8266 height data and do the PATT attestation. |
| TrackPath.txt         |               | Edit the drone fly path.                                     |



------

### Program Usage/Execution

##### Run the Program

Follow the section "WIFI Connection Diagram" to connect to the sensor and drone to your computer. Then execute the program telloRun.py under `src` folder by the below command: 

```
python telloRun.py
```

After the program initialization finished, the below message will show in your terminal: 

```
"Program init finished."
```

 Then the main UI will show as below: 

![](doc/img/mainUI.png)



##### Control the drone, sensor and do the firmware attestation

1. Click the "**UAV Connect**" button under the title line, if the done responses correctly the "drone state" indicator in UI will change to green and the indicator will show "**UAV_Online**".

2. The sensor will connect to the program automatically. When the ESP8266 Arduino connected to the program, the sensor indicator will change to green and show "**SEN_Online**". 

3. Press the white '**Camera**' button under "**Takeoff and Cam Ctrl**" will turn on the drone's front camera.

4. The latest battery reading will be shown on the left-top corner of the front camera view panel and the height of the drone will be shown on the right side of the the lowest skyline horizontal indicator. The battery reading show in the title bar is the average reading in the passed 10 seconds. 

5. Drone track path planning: 
   - Add a track: Open the track record file "`TrackPath.txt`" (under `src` folder)  and add the track by below format:
   
  > TrackName**;**action 1**;**action x**;**action x**;**action x**;**action x**;**action x**;**land (example:*Track1;takeoff;command;up 30;ccw 30;up 30;ccw 30;up 30;land* .

     >  If you don't set the land cmd, the program will add the land cmd automatically. For the action setting part, please check the detail drone control protocol in Tello SDK Documentation EN_1.3_1122.pdf under doc folder ) 

   - Select the track in the drop down menu and click the "**Active track**" button, the selected track will by executed by the drone. The current executed action will be marked as green color. 

6. Sensor Firmware Attestation Control:  

   - Fill attestation times you want to do and the memory block size, then press the "**startPatt**" button. The local firmware and the sensor firmware will be shown and compared. The attestation result and total time used for the attestation process will be shown as below (The attestation process will take about 8sec ~ 10 sec): 

   - ![](doc/img/attestFail.jpg)

   - Every attestation result will be record in the "checkSumRecord.txt" (source folder) under format: 

     checksum record [2019-10-18 12:18:30.305437]:

     Local:`1400A0C126221302030000340C21865C1014050020C0313FBEE0CD0C0B073110FF0C02C174033F4010101C910C38FF7EFFEE0D210D012921020CE00E020012F0`

     Remote:`1400A0C126221302030000340C21865C1014050020C0313FBEE0CD0C0B073110FF0C02C174033F4010101C910C38FF7EFFEE0D210D012921020CE00E020012F0`

     

7. Press the '**>>**' button under the title bar the drone detail status information display window will pop-up on the right.

------

### Problem and Solution

N.A

------

### Reference

PATT firmware attestation: 

https://www.usenix.org/system/files/raid2019-ghaeini.pdf



------

> Last edit by LiuYuancheng(liu_yuan_cheng@hotmail.com) at 29/01/2020