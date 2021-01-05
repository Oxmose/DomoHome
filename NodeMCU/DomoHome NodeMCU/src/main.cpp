#include <Arduino.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>

#define NET_SSID    "DomoDev"
#define NET_PSSWD   "DomohomeDev"
#define NET_TIMEOUT 1000
 
ESP8266WebServer server(80);

void restServerRouting() {
    server.on("/", HTTP_GET, []() {
        server.send(200, F("text/html"),
            F("Welcome to the REST Web Server"));
    });
    
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

void defaultRoute(void) 
{
  String message;

  message = "{ data: {temp: 242.5}, error: 0}";
  
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

  /* Temperature sensore request */
  server.on("/getTemp", HTTP_GET, getTempRoute);
}

void setup(void) 
{
  Serial.begin(9600);

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