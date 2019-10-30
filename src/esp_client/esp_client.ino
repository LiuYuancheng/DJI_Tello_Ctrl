#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>

//-----------------------------------------------------------------------------
// Name:        esp_client.ino
//
// Purpose:     This module will start a TCP client to send the HC-SR04 Ultrasonic
//              Sensor reading to server and send the firmware checksum for attestation. 
//              
// Author:      Sombuddha Chakrava, Yuancheng Liu
//
// Created:     2019/10/21
// Copyright:   YC @ Singtel Cyber Security Research & Development Laboratory
// License:     
//-----------------------------------------------------------------------------

// Set the wifi ssid and pwd.
const char *ssid = "TRD";
const char *password = "St91195921";

// Pins to communicate to the HC-SR04 Ultrasonic sensor.
const int echoPin = 0; //D3
const int trigPin = 2; //D4

int addrCount;  // Num of address will be used to calculate the checksum.
long duration;  // The time betweem send the sound and get the feedback.
const char *host = "192.168.1.100"; // IP serveur - Server IP
const int port = 4000;              // Port serveur - Server Port

//-----------------------------------------------------------------------------
// Init the serial, network communication, all global parameters and OTA.
void setup()
{
  // Init the serial comm.
  Serial.begin(115200);
  Serial.println("Booting");
  // Init network comm.
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    Serial.print(".");
    delay(500);
  }
  Serial.println("Connected to wifi.");
  // Init OTA used functino.
  ArduinoOTA.setPort(8266);// Port defaults to 8266
  ArduinoOTA.onStart([]() {
    if (ArduinoOTA.getCommand() == U_FLASH)
    {
      Serial.println("Start updating sketch");
    }
    else
    { // U_SPIFFS
      Serial.println("Start updating filesystem");
    }
  });
  ArduinoOTA.onEnd([]() {
    Serial.println("\nEnd");
  });
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
  });
  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("Error[%u]: ", error);
    switch (error)
    {
    case OTA_AUTH_ERROR:
      Serial.println("Auth Failed");
      break;
    case OTA_BEGIN_ERROR:
      Serial.println("Begin Failed");
      break;
    case OTA_CONNECT_ERROR:
      Serial.println("Connect Failed");
      break;
    case OTA_RECEIVE_ERROR:
      Serial.println("Receive Failed");
      break;
    case OTA_END_ERROR:
      Serial.println("End Failed");
      break;
    default:
      Serial.println("OTA Pass");
    }
  });
  // Init the paramters.
  ArduinoOTA.begin();
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
  pinMode(echoPin, INPUT);  // Sets the echoPin as an Input
  Serial.println("Ready");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  addrCount = 0;
}

//-----------------------------------------------------------------------------
// main loop.
void loop()
{
  WiFiClient client;
  if (!client.connect(host, port))
  {
    Serial.println("connection failed");
    client.stop();
    delay(200);
    return;
  }
  // hand shake with the server.
  delay(10);
  if (client.connected())
  {
    client.println("hello from ESP8266");
  }
  delay(10);
  // loop to send the distance data.
  while (client.connected())
  {
    // Get the distance data from the sensor.
    ArduinoOTA.handle();
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);
    duration = pulseIn(echoPin, HIGH);
    String dist = String(duration * 0.034 / 2);
    // hole to wait any cmd available from the server.
    while (client.available() == 0)
    {
      if(client.connected())
      {       
        delay(1); 
      }
      else{
        return; // handle the reconnect situation.
      }
    }
    String line = client.readStringUntil('\r');
    line.trim();
    // handle the server cmd. 
    if (addrCount == 0)
    {
      long tmp = line.toInt();
      if (tmp == -1)
      {
        Serial.println(dist);
      }
      else
      {
        addrCount = tmp; // update the addresss count.
      }
      client.print(dist);
    }
    else
    {
      String chsm = ""; // firmware checksum
      for (int i = 0; i < addrCount; i++)
      {
        String sub = getValue(line, ';', i);
        long tmp = sub.toInt();
        uint32_t incomingValue = (uint32_t)tmp;
        Serial.println(incomingValue);
        uint32_t data;
        ESP.flashRead(incomingValue, &data, 1);
        String x = String(data, HEX);
        x = x.substring(x.length() - 2, x.length());
        chsm = chsm + x;
      }
      chsm = chsm + ',' + dist;
      addrCount = 0; // clear the address count.
      client.print(chsm);
    }
  }
}

//-----------------------------------------------------------------------------
// Split a string and return the substring based on the input idx.
String getValue(String data, char separator, int index)
{
  int found = 0;
  int strIndex[] = {0, -1};
  int maxIndex = data.length() - 1;

  for (int i = 0; i <= maxIndex && found <= index; i++)
  {
    if (data.charAt(i) == separator || i == maxIndex)
    {
      found++;
      strIndex[0] = strIndex[1] + 1;
      strIndex[1] = (i == maxIndex) ? i + 1 : i;
    }
  }
  return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}
