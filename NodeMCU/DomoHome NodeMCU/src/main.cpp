#include <Arduino.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>

#define NET_SSID    "DomoDev"
#define NET_PSSWD   "DomohomeDev"
#define NET_TIMEOUT 1000
 
ESP8266WebServer server(80);

bool isGPIOValid(uint8_t gpio)
{
  return (gpio < 6 || (gpio > 11 && gpio < 17));
}

void setPWM(uint8_t gpio, uint8_t value)
{
  uint16_t dutyCycle = (uint16_t)(((float)value / 100.0) * 1023);
  if(dutyCycle > 1023)
  {
    dutyCycle = 1023;
  }
  analogWrite(gpio, dutyCycle);
}

void setRGB(uint8_t gpio[3], uint8_t values[3])
{
  uint16_t dutyCycle;
  uint8_t  i;
  for(i = 0; i < 3; ++i)
  {
    dutyCycle = (uint16_t)(((float)values[i] / 255.0) * 1023);
    if(dutyCycle > 1023)
    {
      dutyCycle = 1023;
    }
    analogWrite(gpio[i], dutyCycle);
  }
  
}

void setToggle(uint8_t gpio, bool value)
{
  pinMode(gpio, OUTPUT);
  digitalWrite(gpio, value ? HIGH : LOW);
}
 
void unknownRoute(void) 
{
  uint8_t i;
  String  message;
  
  message = "Unknown route\n";
  message += "URI: ";
  message += server.uri();
  message += "\nMethod: ";
  message += (server.method() == HTTP_GET) ? "GET" : "POST";
  message += "\nArguments: ";
  message += server.args();
  message += "\n";
  for (i = 0; i < server.args(); ++i) 
  {
    message += " " + server.argName(i) + ": " + server.arg(i) + "\n";
  }
  server.send(404, "text/plain", message);
}

void defaultRoute(void) 
{
  String message;

  message =  "<h1>DomoHome Node</h1>";
  message += "<h2>IP: "; 
  message += WiFi.localIP().toString();
  message += "</h2>";
  
  server.send(200, "text/html", message);
}

void setPWMRoute(void)
{
  String  message;
  uint8_t i;
  uint8_t gpio;
  uint8_t value;

  gpio  = 0xFF;
  value = 0xFF;

  for (i = 0; i < server.args(); ++i) 
  {
    if(server.argName(i) == "gpio")
    {
      gpio = server.arg(i).toInt();
    }
    else if(server.argName(i) == "value")
    {
      value = server.arg(i).toInt();
    }
    else 
    {
      message = String("{error: 1, msg: \"Unknown argument: ") + server.argName(i) + String("\"}");
      break;
    }
  }

  if(i == server.args())
  {
    if(!isGPIOValid(gpio)) 
    {
      message = String("{error: 2, msg: \"Invalid GPIO: ") + String(gpio) + String("\"}");
    }
    else if(value > 100)
    {
      message = String("{error: 2, msg: \"Invalid value: ") + String(value) + String("\"}"); 
    }
    else 
    {
      message = String("{error: 0, msg: \"Success\"}");
      setPWM(gpio, value);
    }
  }

  server.send(200, "text/json", message);
}

void getToken(uint8_t* tokens, uint8_t count, String str, char sep)
{
  uint8_t  i;
  uint32_t lastPos;
  uint8_t  found;

  lastPos = 0;
  found   = 0;
  for(i = 0; i < str.length(); ++i)
  {
    if(str[i] == sep)
    {
      tokens[found] = str.substring(lastPos, i).toInt();
      lastPos = i + 1;
      ++found;
    }
    else if(i == str.length() - 1)
    {
      tokens[found] = str.substring(lastPos, i + 1).toInt();
      ++found;
    }

    if(found == count)
    {
      break;
    }
  }
}

void setRGBRoute(void)
{
  String  message;
  uint8_t i;
  uint8_t error;
  uint8_t gpio[3] = {0xFF, 0xFF, 0xFF};
  uint8_t values[3] = {0xFF, 0xFF, 0xFF};

  for (i = 0; i < server.args(); ++i) 
  {
    if(server.argName(i) == "gpio")
    {
      getToken(gpio, 3, server.arg(i), '_');
    }
    else if(server.argName(i) == "value")
    {
      getToken(values, 3, server.arg(i), '_');
    }
    else 
    {
      message = String("{error: 1, msg: \"Unknown argument: ") + server.argName(i) + String("\"}");
      break;
    }
  }

  error = 0;
  if(i == server.args())
  {
    for(i = 0; i < 3; ++i)
    {
      if(!isGPIOValid(gpio[i])) 
      {
        message = String("{error: 2, msg: \"Invalid GPIO: ") + String(gpio[i]) + String("\"}");
        error = 1;
        break;
      }
      else if(values[i] > 255)
      {
        message = String("{error: 2, msg: \"Invalid value: ") + String(values[i]) + String("\"}"); 
        error = 1;
        break;
      }
    }
    
  }

  for(i = 0; i < 3; ++i)
  {
    Serial.println(values[i]);
    Serial.println(gpio[i]);
  }
  

  if(error == 0) 
  {
    message = String("{error: 0, msg: \"Success\"}");
    setRGB(gpio, values);
  }

  server.send(200, "text/json", message);
}

void setToggleRoute(void)
{
  String  message;
  uint8_t i;
  uint8_t gpio;
  uint8_t value;

  gpio  = 0xFF;
  value = 0xFF;

  for (i = 0; i < server.args(); ++i) 
  {
    if(server.argName(i) == "gpio")
    {
      gpio = server.arg(i).toInt();
    }
    else if(server.argName(i) == "value")
    {
      value = server.arg(i).toInt();
    }
    else 
    {
      message = String("{error: 1, msg: \"Unknown argument: ") + server.argName(i) + String("\"}");
      break;
    }
  }

  if(i == server.args())
  {
    if(!isGPIOValid(gpio)) 
    {
      message = String("{error: 2, msg: \"Invalid GPIO: ") + String(gpio) + String("\"}");
    }
    else if(value == 0xFF)
    {
      message = String("{error: 3, msg: \"Value not set\"}");
    }
    else 
    {
      message = String("{error: 0, msg: \"Success\"}");
      setToggle(gpio, value != 0);
    }
  }

  server.send(200, "text/json", message);
}

void initConnection(void)
{
  /* Set mode and network data */
  WiFi.mode(WIFI_STA);
  WiFi.begin(NET_SSID, NET_PSSWD);

  Serial.println("Connection to " NET_SSID);

  /* Wait for connection */
  while (WiFi.status() != WL_CONNECTED) 
  {
    delay(NET_TIMEOUT);
    Serial.print(".");
  }

  Serial.println("\nConnected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void initServerRouting(void)
{
  /* On erroneous route */
  server.onNotFound(unknownRoute);

  /* Default route */
  server.on("/", HTTP_GET, defaultRoute);

  /* Set toggle value */
  server.on("/setToggle", HTTP_GET, setToggleRoute);

  /* Set PWM value */
  server.on("/setPWM", HTTP_GET, setPWMRoute);

  /* Set RGB value */
  server.on("/setRGB", HTTP_GET, setRGBRoute);
}

void setup(void) 
{
  /* Init serial */
  Serial.begin(9600);

  /* Init PWM frequency */
  analogWriteFreq(500);

  /* Init network connection */
  initConnection();
 
  /* Init the server's API handling */
  initServerRouting();

  /* Init server */
  server.begin();
  Serial.println("DomoHome node ready");
}
 
void loop(void) 
{
  server.handleClient();
}