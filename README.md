# DJI_Tello_Control_System Cyber Attack Case Study [Drone Firmware Attack and Detection]

**Program Design Purpose**: The objective of this cyber attack case study is aim to develop a workshop using the terrain-matching drone system and dynamic firmware attestation algorithm introduced in paper [PAtt: Physics-based Attestation of Control Systems](https://www.usenix.org/system/files/raid2019-ghaeini.pdf) to illustrate a practical demonstration of OT/IoT device firmware attack and the corresponding attack detection mechanisms. The terrain-matching drone is built by one Arduino, four distance sensors and one DJI Tello un-programable drone. The attack scenario involves a red team attacker injecting malicious code into the drone's terrain contour generation unit firmware, disrupting the drone auto landing process, and leading to a simulated drone crash. Simultaneously, the case study also showcases how blue team defenders employ the PATT firmware attestation function to identify the firmware attack in real-time, preventing the accident and highlighting the importance of robust defense mechanisms in securing operational technology and internet of things devices.

**Attacker Vector** : Firmware Attack, Malicious Firmware Updates (OT), IoT Supply Chain Attacks

> Important : The demonstrated attack case is used for education and training for different level of IT-OT cyber security ICS course, please don't apply it on any real world system.

[TOC]

------

### Introduction

This case study aims to develop a smart drone system capable of emulating specific Industry 4.0 (I4.0) drone autopilot use case, including autonomously tracing routes, environment sensing (Terrain matching), transfer items and making decisions for subsequent actions. The objective is to demonstrate the potential impact of an Operational Technology (OT) firmware attack on such a system. The project is structured into three key sections:

- **Attack Demo Platform:** Utilizing the DJI Tello Terrain Matching Drone System as the foundation platform for showcasing autopilot functionalities, potential vulnerabilities and attack scenario.
- **Firmware Attack Demonstration :** Focusing on a demonstration of a malicious firmware update attack targeting the drone's Ground Contour Map Generate Unit. This simulation will highlight the consequences of a malicious intrusion affecting the system's ability to perform tasks effectively.
- **Attack Detection and Defense:** Implementing Physics-based Firmware Attestation as a means of illustrating how a robust defense mechanism can detect and mitigate the impact of a firmware attack. This section emphasizes the significance of proactive security measures in safeguarding drone systems within an Industry 4.0 context.



#### DJI Tello Terrain Matching Drone Control 

In this project, our aim is to enhance the capabilities of the DJI Tello mini drone, which is inherently unprogrammable, in order to simulate actions commonly performed by industry drones, such as following predefined routes and transporting items within a factory setting. The DJI Tello drone, being a basic unprogrammable model, requires additional features to emulate more complex tasks. To achieve this, we have integrated four additional ultrasonic sensors onto the drone, enhancing its ability to "detect" a more intricate environment. The autopilot control is executed by a main drone control program running on the connected computer.

The bottom sensor of the DJI Tello, along with the four added distance sensors, collaborates to generate a comprehensive "5 points" ground contour map of the drone's surroundings. The primary drone controller, housed on the control computer, orchestrates the drone's movements to simulate autopilot actions and follow predefined routes based on the acquired contour map data.

The bottom sensor of the DJI Tello, along with the four added distance sensors, collaborates to generate a comprehensive "5 points" ground contour map of the drone's surroundings. The primary drone controller, housed on the control computer, orchestrates the drone's movements to simulate autopilot actions and follow predefined routes based on the acquired contour map data. For instance, if the objective is to make the drone fly straight until it detects an object resembling a table beneath it, and then proceed to land on that table (simulating the transfer of items from one table to another), the drone continually transmits the contour map to the control program. The drone control program analyzes the received contour matrix and if it matches the predefined features of a table, it will issue the landing command to the drone. The typical terrain matching process is illustrated below:

![](doc/img/terrain_match.png)

>  **Remark**: In the program design section of this document, we will provide a detailed overview of the DJI Tello Drone controller program. This comprehensive discussion will cover essential aspects, including the intricate usage of drone basic motion control, the functionality of track editing, the ground simple contour matching process, and the drone motion safety check function. This information is intended to empower users with the necessary insights and tools to plan and execute complex routes for the drone, ensuring a seamless and safe operation.



#### Firmware Attack Demonstration 

In this malicious firmware updates attack scenario, the red team attacker's target is the firmware program running on the drone's CMGU (contour map generation unit).  CMGU is crucial for fly environment monitoring and terrain matching, it comprises an ESP8266 Arduino, a battery, and four HC-SR04 Ultrasonic Sensors. During the attack demo, the red team attacker did exploiting a vulnerability in the IoT supply chain, sent a deceptive firmware update email to a negligent drone maintenance engineer, resulting in the installation of the malicious firmware in the contour map generation unit. The attack underscores the critical importance of securing the IoT supply chain to prevent unauthorized firmware alterations and potential operational disruptions. The attack path is shown below : 

![](doc/img/attackPath.png)

The rogue firmware behaves inconspicuously during manual drone control or when following predefined routes. However, it activates malicious functionalities when the drone initiates autopilot mode for ground contour matching. Specifically, the firmware introduces random "noisy" distance data, deliberately distorting the accuracy of ground contour information. This misinformation misguides the drone controller, leading to incorrect decision-making and, consequently, drone accidents such as crashes. 

> The detail demo video : https://youtu.be/rRu1qrZohJY?si=g5fkKZf4Z8Osre6I



#### Arduino Firmware Attestation

In this segment, we will illustrate how a drone operator can employ the dynamic, real-time firmware attestation to not only detect the attack but also prevent potential accidents involving the drone. To achieve this, we adopt a portion of the PLC firmware attestation algorithm outlined in the paper "PATT"( Physics-based Attestation of Control Systems) to verify whether the firmware attack has happened. We will follow the "Nonce Storage and Hash Computation" part introduced in the paper to dynamically calculate the firmware's hamming hash with the `k=4` as shown below :

![](doc/img/paper.png)

It's essential to express our thanks for the Physics-based Attestation of Control Systems paper authors Dr.Hamid Reza Ghaeini and Professor Jianying Zhou from [SUTD](https://www.sutd.edu.sg/) for introducing the efficient and robust firmware attestation algorithm. 

> Physics-based Attestation of Control Systems paper link: https://www.usenix.org/system/files/raid2019-ghaeini.pdf



#### Key Tactics, techniques, and procedures (TTP) of the attack

Based on the attack detailed road map introduced in the attack demo section, there will be two kinds main TTP included in the firmware attack scenario : 

##### Malicious Firmware Development

- **Tactic:** Develop customized firmware with malicious functionality.
- **Technique:** Modify existing firmware or create new firmware that includes backdoors, exploits, or other malicious code.
- **Procedure:** The red team attacker modified the normal drone's terrain-matching unit's firmware by inserting malicious code into the firmware without detection, ensuring it remains hidden and does not trigger security mechanisms.

##### Supply Chain Compromise

- **Tactic:** Compromise the drone's firmware during the manufacturing or distribution process.
- **Technique:** Infiltrate the supply chain to insert malicious firmware before the drone reaches end-users.
- **Procedure:** The red team attacker builds a fake software update server web site and send the link to the drone maintenance engineer via a deceptive drone firmware update email to introduce and inject the compromised firmware into the supply chain. The web will also provide the malicious firmware's MD5 value for the maintenance engineer to verify the unauthorized firmware update package. 



------

### Background Knowledge 

Within this section, we aim to provide fundamental, general knowledge about each respective system and elucidate the Tactics, Techniques, and Procedures (TTP) associated with the attack vectors. This foundational information will serve as a primer for understanding the intricate details of the systems involved and the methodologies employed in the attack scenarios.

#### DJI Tello Drone Control and Terrain Matching 

Before we introduce the attack technology background knowledge, we need to introduce the plant form we build for our attack case, the DJI Tello Drone Terrain Matching system.  

To change a normal unprogrammable drone to be a "smart" drone. We installed four HC-SR04 Ultrasonic Sensors under the DJI Tello Drone (as shown below), then we use a ESP8266 Arduino's GPIO pin (`GPIO5-D1`, `GPIO4-D2`, `GPIO0-D3` and `GPIO2-D4`) to connect to the sensor's data positive (+) pin. Then the contour map generation code running on  Arduino will read the distance data and average the data to get a stable 4 points drone bottom area contour map every 0.5 second.

![](doc/img/droneConnectrion.png)

We also provide a control program with all the trojan flight control function. The  ESP8266 will send the 4 points drone bottom area contour map back to the control program and combine with the drone's bottom height sensor's reading, then we build a 5 points drone bottom area contour map as shown below: 

![](doc/img/TerrainMatching.png)

The drone controller's Terrain Matching module will compare the final drone bottom area contour map with its pre-saved contour map matrix, if the difference is under the threshold, then the control program will detect the "Terrain Matched", after the Terrain Matched last for 2 seconds, the control will send the pre-set the flight action time line (rout plat book) to the drone. (such as instruct the drone landing on the surface)



#### Firmware Attack

A **firmware attack** is any malicious code that enters your device by using a backdoor in the processor’s software. Backdoors are paths in the code, which allow certain individuals to bypass security and enter the system. The backdoor normally goes undetected due to its intense complexity, but can result in serious consequences if exploited by [hackers](https://netacea.com/blog/crackers-arent-hackers/).

A common example of a firmware attack is an unauthorized update on your computer or phone that results in [malware](https://netacea.com/glossary/malware/) or some other form of cybercriminal activity. This is because many updates include backdoors with undocumented features or functions that can be used for adverse actions, such as intercepting data without notice and turning off core functionalities; all while still masquerading itself as an innocent update process.

>  Reference link: https://netacea.com/glossary/firmware-attack/

During the attack demo, the red team attacker's target is the firmware of the ground contour generate unit (as shown in the pre-section), the attack will add malicious code in the distance sensor data reading part to add the random offset of the real data to mess up the ground contour generation result. Before the attack, the drone will fly straight until till find another table which match its pre-saved ground contour (identify as a safe landing plan) then land on the table. After the firmware attack, after messed up the ground contour generation result, a unsafe place's contour matrix data will be identify as a matching result, the the drone will try to land and crash. (As shown in the demo video) 



#### PAtt: Physics-based Attestation of Control Systems

PAtt is designed to allow remote attestation of logic code running on a PLC without a traditional trust anchor (such as a TPM or PUF), For the PAtt: Physics-based Attestation of Control Systems please refer to  Dr.Hamid Reza Ghaeini and Professor Jianying Zhou's Paper: https://www.usenix.org/system/files/raid2019-ghaeini.pdf

In our project we followed We will follow the "Nonce Storage and Hash Computation" part introduced in the paper to dynamically calculate the firmware's hamming hash with the `k=4` to verify the firmware running on ESP8266 Arduino. 



------

### System Design 

In this section we will introduce four main section design of the system:

- Drone Controller UI design
- Communication Protocol Design 
- Design of Malicious Code and the Firmware Attack
- Design of the Firmware Attestation 

The drone controller main thread will start three parallel sub-threads to communicate with the Arduino to fetch the data and do the firmware attestation,read the Tello states data and get the Tello's UDP Video stream. The main thread will handle the Tello control.



#### Drone Controller UI design 

The drone controller user interface contents four main panel as shown below:

![](doc/img/uidesign.png)

The Drone control UI contents 6 different function panel: 

- **Drone state panel** : Top panel of the UI to allow the drone operator to select drone, check the drone connection and battery state, the ground contour generate unit connection state, firmware attestation state and view the drone front camera. 
- **Drone flight control panel** : Drone manual flight control panel to control the drone's vertical / horizontal movement , row pitch yaw adjustment, take off and landing and the camera on / off. 
- **Drone autopilot control panel** : Panel for drone operator to control the drone to auto follow the pre-set rack, edit/load track config file, load the terrain matching config file, display the way point and auto action detail.  
- **Ground contour generator info panel**: Panel to show all the drone's sensor feed back data and the Ground contour generate unit feed back data.
- **PATT parameter config panel** : Panel for the drone operator to config the firmware PATT Hash calculation parameters and start one round attestation progress. 
- **PATT result display panel** : panel to show attestation progress with a progress bar and show the local PATT Hash calculation result and the drone side firmware PATT Hash result when the attestation finished.



#### Communication Protocol Design 

The Drone control computer will connect to the drone via 2 WIFI link: 

- **Drone communication link** : the drone provide a WIFI AP itself, so the controller will connect to the drone directly via WIFI to control the drone. 
- **Ground contour generator link**: the ESP8266 Arduino's a WIFI module to connect to a WIFI AP, so the it will login to the WIFI router which connect to the control computer by Ethernet cable.

![](doc/img/connection.png)

As shown in the above diagram, there are 4 wireless communication channel between the drone controller computer and the Drone. The control hub (Computer) will control with the drone by UDP and fetch the feedback data of Ground contour generator by TCP as shown below:

![](doc/img/port.png)

| Channel Name                          | Data flow                                                    | Target                     | Protocol       | Port  |
| ------------------------------------- | ------------------------------------------------------------ | -------------------------- | -------------- | ----- |
| Ground contour generator data channel | Fetch the ground contour matrix data from sensor             | Arduino_IP (192.168.1.101) | TCP            | 4000  |
| Drone motion control channel          | Send drone flight controm Command & Receive Response         | Tello_Drone(192.168.10.1)  | UDP            | 8889  |
| Drone sensor data channel             | Fetch drone built in bottom height sensor, flight sensor, battery , gyroscope data | Tello_Drone(192.168.10.1)  | UDP            | 8890  |
| Drone Video channel                   | Drone front camera video                                     | Tello_Drone(192.168.10.1)  | UDP H264 video | 11111 |

The gound contour generator firmware attestation communication shared the same channel with the Ground contour generator data channel, so when the attestation start, the Ground contour generation function will temporary paused and the channel will be used for transfer the PATT data. 

| The program will connect to the Arduino by TCP and communicate with the drone by UDP |
| ------------------------------------------------------------ |
| **Arduino  Control**:  Arduino_IP: 192.168.1.101, TCP_PORT: 4000 <<- ->>  PC_IP: 192.168.1.100 TCP_PORT: 4000 |
| **Drone Control** (Send Command & Receive Response):  Tello_IP: 192.168.10.1  UDP_PORT:8889  <<- ->>  PC/Mac/Mobile_IP: 192.168.10.xx UDP_PORT:8889 |
| **Drone Control** (Receive Tello State): Tello_IP: 192.168.10.1  UDP_PORT:8890 ->>  PC/Mac/Mobile_ UDP_Server: 0.0.0.0, UDP PORT:8890 |
| **Drone Control** (Receive Tello Video Stream) :  Tello_IP: 192.168.10.1, UDP_PORT:11111->>  PC/Mac/Mobile_UDP_Server: 0.0.0.0,  UDP_PORT:11111 |



#### Design of Malicious Code and the Firmware Attack 

The red team attacker will follow below step to do the firmware attack

The red team attacker download the normal firmware file `esp_client.ino.generic.bin` from authorized firmware server.  

red team attacker user reverse engineer tool decompiled the binary to get part of the firmware C++ source code. 

Then he analysis the code find the way to calculate the distance is we use the sensor generate a sound pulse, then measured the time interval between send the pulse and get the echo, then we multiple the time with the speed of sound and divided by 2. After he understand of the logic, the red team attacker added the malicious code in is as shown below: 

![](doc/img/maliciousCode.png)

As shown in the malicious code the attacker added a random delay (0 ~300 microsec) before and after the pulse to make the echo time not consistent, then also add a random value (-3, 8) to the distance result make the final result have a random offset between -30cm to 80 cm. 

After added the malicious code, the attacker repackage the fake firmware and send to the drone maintenance engineer via a fake ground contour generate unit firmware update email. 

The maintenance engineer load the firmware to the ground contour generate unit, and he turn on the power and there some feedback data and as he didn't make the drone take off the distance data "looks" ok, so he thought the firmware is working normally which is actually not. As shown below,  the difference of the contour map send back to the controller :

![](doc/img/attackCompare.png)

When the drone operator uses the drone to do some task such as transfer some thing from one table to another table, when the drone take off, its ground contour generate unit keep generate fake distance data which caused the drone landing on the ground or crash. 



#### Design of the Firmware Attestation 

To verify the firmware, both the control computer side will keep a copy of valid firmware and simulate the firmware loading to memory which same as the Arduino. The detailed attestation steps are shown below: 

- When we start to do the firmware attestation, the controller will fetch the firmware version and serial number from the Arduino. Based on the firmware version and serial number the control program will go to its data base to fetch the related firmware, firmware memory config and the random memory addresses list generation function from its data base.  
- After fetched all the related information, the controller side will generate a "twin" memory map which is same as the target memory and load the firmware in the memory. After this prepare works done, it will create a random seed and send the seed to the Arduino. 
- Both controller and the firmware side will used the same random seed and the random memory addresses list generation function to generate a random memory address list. After the list finished both controller side and the Arduino will calculate the Ham(a, b) for every address in the address list. Assume a address in the list is `0x7FFF5FBFFD98` "a" is the contents in from `0x7FFF5FBFFD98`  to `0x7FFF5FBFFD98+k` , after all the Ham(a,b) are calculated, we will combine all the Ham(a,b) together and get the hash value to do one round iteration. Based on the iteration parameter setting, after finish all the iteration,  all the hash value will combined together to generate the PATT checksum value. 
- The Arduino will send back the PATT checksum back to the controller though the ground contour channel , if the send back checksum is same as the controller's checksum, the firmware attestation is passed, else firmware attack will be detected. 

The main communication flow is shown below (System execution workflow UML diagram) :

![](doc/img/workflow.png)



------

### Program Setup

###### Development Environment

> Python 3.7.4, C++

###### Additional Lib Need

1. wxPython 4.0.6 (need to install for UI building) [> link](https://wxpython.org/pages/downloads/index.html:)

```
pip install -U wxPython 
```

2. OpenCV: opencv-python 4.1.1.26  (need to install to do the H264 video stream decode) [> link](https://pypi.org/project/opencv-python/)

```
pip install opencv-python
```

###### Hardware Need

We use DJI Tello Drone, ESP8266 Arduino and HC-SR04 Ultrasonic Sensor to build the system: 

![](doc/img/item.jpg)

- **DJI Tello Drone** : DJI tello control SDK [> link ](https://www.ryzerobotics.com/tello/downloads ) 
- **ESP8266 Arduino** : ESP8266 Arduino dev doc [> link](https://arduino-esp8266.readthedocs.io/en/latest/)
- **HC-SR04 Ultrasonic Sensor** : Product features doc [> link](https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf)



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

##### Load the ground matric file

To active the Terrain Matching function, the operate needs to change the config file's Terrain Matching flag to `True` after that when start the UI, the loading button will show up. Then Press the "loadCont" button the count file will pop up. 

![](doc/img/loadContour.png)

select the contour file you want to match, one simple contour example is shown below:

```
{
	"sensorLF"	: [1.33, 1.23]	# The drone left front sensor reading 
	"sensorLB"	: [1.33, 1.24] 	# the drone left back sensor reading	
	"sensorMD"	: [1.12, 1.20]	# the fone mid height sensor reading
	"sensorRF"	: [1.33, 1.23] 	# The drone right front sensor reading 
	"sensorRB"	: [1.33, 1.24] 	# the drone right back sensor reading
	"threshold" : 0.15			# matching threshod
	"matchingT" : 2				# time to trigger matching (second)
	"tackID"	: "trackLanding" # track to be executed after terrain matched.
}
```



##### Control the drone, sensor and do the firmware attestation

The drone operator can do the attestation during the drone is flying, but we recommend drone operator do the attestation before the drone take off. The detailed step to do one attestation is shown below:

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

   - ![](doc/img/attestationRst.png)

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

> Last edit by LiuYuancheng(liu_yuan_cheng@hotmail.com) at 03/01/2024

