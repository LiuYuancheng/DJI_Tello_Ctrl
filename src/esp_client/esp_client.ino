#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>
// Set the wifi ssid and pwd.
const char *ssid = "TRD";
const char *password = "St91195921";
//Attacking the drone
const int echoPin = 0; //D3
const int trigPin = 2; //D4

int distance;
int addrCount;
long duration;

const char *host = "192.168.1.100"; // IP serveur - Server IP
const int port = 4000;              // Port serveur - Server Port
const int watchdog = 200;           // Fréquence du watchdog - Watchdog frequency
unsigned long previousMillis = millis();
unsigned long askTimer = 0;

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
  Serial.println("Connected to wifi:");
  // Port defaults to 8266
  ArduinoOTA.setPort(8266);
  // Start OTA
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
  // End OTA
  ArduinoOTA.onEnd([]() {
    Serial.println("\nEnd");
  });

  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
  });

  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("Error[%u]: ", error);
    switch(error){
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

  ArduinoOTA.begin();
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
  pinMode(echoPin, INPUT);  // Sets the echoPin as an Input
  Serial.println("Ready");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  addrCount = 0;
}

void loop()
{
  WiFiClient client;
  unsigned long currentMillis = millis();

  if (!client.connect(host, port))
  {
    Serial.println("connection failed");
    client.stop();
    delay(200);
    return;
  }
  delay(10);

  if (client.connected()) {
    client.println("hello from ESP8266");
  }
  delay(10);

  while(client.connected())
  {
    ArduinoOTA.handle();
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);
    duration = pulseIn(echoPin, HIGH);
    String dist = String(duration * 0.034 / 2);
    while (client.available()== 0)
      {
        delay(1);
      }
    String line = client.readStringUntil('\r');
    line.trim();

    if(addrCount == 0){
      long tmp = line.toInt();
      if (tmp == -1)
      {
        Serial.println(dist);
        client.print(dist);
      }
      else{
        addrCount = tmp;
      }
    }
    else
    {
      String chsm = "";
      for (int i = 0; i < addrCount; i++) {
        String sub  = getValue(line,';',i);
        long tmp = sub.toInt();
        uint32_t incomingValue = (uint32_t)tmp;
        Serial.println(incomingValue);
        uint32_t data;
        ESP.flashRead(incomingValue, &data, 1);
        String x = String(data, HEX);
        x = x.substring(x.length() - 2, x.length());
        chsm = chsm + x;
      }
      chsm = chsm +','+dist;
      addrCount = 0; // clear the address count.
      client.print(chsm);
    }
  }
}

String getValue(String data, char separator, int index)
{
  int found = 0;
  int strIndex[] = {0, -1};
  int maxIndex = data.length()-1;

  for(int i=0; i<=maxIndex && found<=index; i++){
    if(data.charAt(i)==separator || i==maxIndex){
        found++;
        strIndex[0] = strIndex[1]+1;
        strIndex[1] = (i == maxIndex) ? i+1 : i;
    }
  }
  return found>index ? data.substring(strIndex[0], strIndex[1]) : "";
}
