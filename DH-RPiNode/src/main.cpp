/**
 * NodeMCU client code.
 *
 * Developped for the DomoHome projet.
 *
 * Alexy Torres Aurora Dugo
 */

#include <Arduino.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <DHT.h>
#include <DHT_U.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <NTPClient.h>
#include <WiFiUdp.h>

#define NET_SSID    "DomoDev"
#define NET_PSSWD   "DomohomeDev"
#define NET_TIMEOUT 500

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET     -1

#define NTP_SERVER "pool.ntp.org"
#define TIME_OFFSET 2
#define DAYLIGHT_SAVING_TIME 1

#define DISP_REFRESH_TIME 500     // 500ms
#define NTP_UPDATE_TIME   3600000 // 1H

#define DEBOUNCE_TIME 100

/* Server objets */
ESP8266WebServer restServer(5001);
DHT_Unified dhtSensor(D7, DHT22);
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
uint64_t requestCount = 0;
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, TIME_OFFSET);

float lastTemp;
float lastHumidity;
uint32_t lastLum;

uint32_t lastRefresh;
uint32_t lastNTPUpdate;

uint64_t curTimestamp;

uint32_t disEnableTime;
bool     displayState;

uint32_t debLastSample;
uint8_t  lastBtnState;


void updateDisplay(void);

/******************************************************************************
 * REST API ROUTES
 *****************************************************************************/
void unknownRoute(void)
{
  uint8_t i;
  uint8_t argsCount;
  String  message;

  message = "{error: 404, msg: \"Unknown route\", ";
  message += "uri: ";
  message += restServer.uri();
  message += ", method: \"";
  message += (restServer.method() == HTTP_GET) ? "GET" : "POST";
  message += "\", arguments: ";
  message += restServer.args();
  message += ", args: \"";

  argsCount = restServer.args();
  for (i = 0; i < argsCount; ++i)
  {
    message += restServer.argName(i) + ": " + restServer.arg(i);
    if(i != argsCount - 1)
    {
      message += ", ";
    }
  }
  message += "\"}";
  restServer.send(404, "text/json", message);

  ++requestCount;
}

void defaultRoute(void)
{
  String message;

  message =  "<h1>DomoHome Node</h1>";
  message += "<h2>IP: ";
  message += WiFi.localIP().toString();
  message += "</h2>";
  message += "<h3>Available routes: </h3>";
  message += "<ul>";
  message += "<li>getEnv</li>";
  message += "</ul>";

  restServer.send(200, "text/html", message);

  ++requestCount;
}

/******************************************************************************
 * MAIN
 *****************************************************************************/
void getLumTempHum(bool isManual)
{
  String          message;
  sensors_event_t event;
  uint32_t        lum;

  float t;
  float h;

  /* Get luminosity */
  lum = analogRead(A0);
  lum = lum * 100 / 1023;

  /* Get temperature and humidity */
  dhtSensor.temperature().getEvent(&event);
  t = event.temperature;
  dhtSensor.humidity().getEvent(&event);
  h = event.relative_humidity;

  /* Update last values */
  lastLum      = lum;
  lastTemp     = t;
  lastHumidity = h;

  message =  "{ \"error\": 0, \"lum\": " + String(lum) + ", \"temp\": " +
                                   String(t) + ", \"humidity\": " +
                                   String(h) + ", \"timestamp\": " +
                                   String(curTimestamp / 1000) + "}";

  if(!isManual)
  {
    restServer.send(200, "text/json", message);
    ++requestCount;
  }
}

void getLumTempHumRest(void)
{
  getLumTempHum(false);
}


void btnPoll(void)
{
  uint8_t  state;
  uint32_t curTime;

  curTime = millis();
  state   = digitalRead(D5);

  if(lastBtnState != state)
  {
    /* Debounce time, manages when millis overflows */
    if(debLastSample + DEBOUNCE_TIME <= curTime ||
       debLastSample > curTime + DEBOUNCE_TIME);
    {
      debLastSample = curTime;
      lastBtnState  = state;

      /* Button is pressed on LOW */
      if(state == 0)
      {
        displayState = !displayState;

        Serial.printf("Display: %d\n", displayState);

        if(displayState)
        {
          display.ssd1306_command(SSD1306_DISPLAYON);
        }
        else
        {
          display.ssd1306_command(SSD1306_DISPLAYOFF);
        }
      }

    }
  }
}

void initDisplay(void)
{
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;);
  }
  display.display();
  delay(100);
  display.setTextColor(WHITE);
  display.setTextSize(1);
  display.clearDisplay();
  display.setCursor(0, 0);
  display.display();
}

void getTime(String& str)
{
  uint32_t hours;
  uint32_t minutes;
  uint32_t seconds;

  hours = (curTimestamp % 86400000L) / 3600000;
  str = hours < 10 ? "0" + String(hours) + ":" : String(hours) + ":";

  minutes = (curTimestamp % 3600000) / 60000;
  str += minutes < 10 ? "0" + String(minutes) + ":"  : String(minutes) + ":";

  seconds = curTimestamp % 60000 / 1000;
  str += seconds < 10 ? "0" + String(seconds) : String(seconds);
}

const char* getSignalStrength(void){
  int8_t dBm;

  dBm = WiFi.RSSI();

  if (dBm >= -46) {
    return "EXCEL";
  }
  if (dBm >= -60) {
    return "GREAT";
  }
  if (dBm >= -72) {
    return "OK";
  }
  if (dBm >= -80) {
    return "WEAK";
  }
  if (dBm >= -90) {
    return "LOW";
  }
  return "DISC";
};

void updateDisplay(void)
{
  String   formattedDate;

  if(displayState)
  {
    /* Clear composition */
    display.clearDisplay();
    display.setCursor(0, 0);

    /* Print wifi status */
    display.printf("%s|%s\n",
                  WiFi.localIP().toString().c_str(),
                  getSignalStrength());

    /* Get time */
    getTime(formattedDate);
    display.printf("%s\n", formattedDate.c_str());

    /* Display info */
    display.printf("Requests: %llu\n", requestCount);
    display.printf("Last data: \n%.1fC | %.1f%% | %u%%\n",
                  lastTemp, lastHumidity, lastLum);

    display.display();
  }
}

void initConnection(void)
{
  /* Set mode and network data */
  WiFi.mode(WIFI_STA);
  WiFi.begin(NET_SSID, NET_PSSWD);

  Serial.println("\nConnection to " NET_SSID);
  display.println("Connection to " NET_SSID);

  /* Wait for connection */
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(NET_TIMEOUT);
    Serial.print(".");
    display.printf(".");
    display.display();
  }

  Serial.println("\nConnected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  updateDisplay();
}

void initServerRouting(void)
{
  /* On erroneous route */
  restServer.onNotFound(unknownRoute);

  /* Default route */
  restServer.on("/", HTTP_GET, defaultRoute);

  /* Read environment */
  restServer.on("/getEnv", HTTP_GET, getLumTempHumRest);
}

void setup(void)
{
  lastRefresh   = 0;
  lastNTPUpdate = NTP_UPDATE_TIME;
  requestCount  = 0;
  lastLum       = -1;
  lastHumidity  = -1;
  lastTemp      = -1;
  displayState  = true;
  debLastSample = 0;

  /* Init serial */
  Serial.begin(9600);

  /* Init DHT sensor */
  dhtSensor.begin();

  /* Init display */
  initDisplay();

  /* Init network connection */
  initConnection();

  /* Init the server's API handling */
  initServerRouting();

  /* Init input button */
  pinMode(D5, INPUT_PULLUP);
  lastBtnState = digitalRead(D5);

  /* Init server */
  restServer.begin();
  Serial.println("DomoHome node ready");
}

void loop(void)
{
  uint32_t curTime;

  /* Wait for request */
  restServer.handleClient();

  /* Get current time */
  curTime = millis();

  /* Refresh display and update time locally */
  if(curTime >= lastRefresh && curTime - lastRefresh >= DISP_REFRESH_TIME)
  {
    curTimestamp += curTime - lastRefresh;
    lastRefresh = curTime;
    getLumTempHum(true);
    updateDisplay();
  }
  /* Check if we need to contact NTP to get the time */
  else if(curTime < lastRefresh || curTime - lastNTPUpdate > NTP_UPDATE_TIME)
  {
    /* Init NTP server */
    timeClient.begin();

    while(!timeClient.update())
    {
      timeClient.forceUpdate();
    }

    curTimestamp = (uint64_t)timeClient.getEpochTime() * 1000ULL + TIME_OFFSET * 3600000;

    /* End NTP server */
    timeClient.end();

    lastRefresh   = curTime;
    lastNTPUpdate = curTime;
    getLumTempHum(true);

    updateDisplay();
  }

  /* Handle button */
  btnPoll();
}
