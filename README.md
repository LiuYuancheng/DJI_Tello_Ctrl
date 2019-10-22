# DJI_Tello_Ctrl

This project will create DJI Tello Drone controller program. It also use the ESP8266 Arduino to read the data from HC-SR04 Ultrasonic Sensor to do the the fly environment monitoring function. It also provide the sensor firmware attestation function by using the "PATT" algorithm.  

Program Main UI View: 

![](https://github.com/LiuYuancheng/DJI_Tello_Ctrl/blob/master/doc/2019-10-18_123002.jpg)

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

1. 



###### View:

![](https://github.com/LiuYuancheng/DJI_Tello_Ctrl/blob/master/doc/sernsors.JPG)

###### Main UI:

![](https://github.com/LiuYuancheng/DJI_Tello_Ctrl/blob/master/doc/mainUI.png)

###### Program execution:

