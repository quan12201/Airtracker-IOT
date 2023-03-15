//Include the library
#include <WiFi.h>
#include <MQUnifiedsensor.h>
#include <PubSubClient.h>

// ESP32 Hostname
String hostname = "ESP32.MQ135";

// Network Credentials
const char* ssid = "iPhone (10)";
const char* pass = "12345678";

#define Sensor_id "13"

#define MQTT_SERVER "broker.hivemq.com"
#define MQTT_PORT 1883
#define MQTT_USER "quan"
#define MQTT_PASSWORD "123456789"
#define MQTT_LDP_TOPIC "mq135"

int current_ledState = LOW;
int last_ledState = LOW;

//Definitions
#define placa "ESP-32"

// Voltage 5v
#define Voltage_Resolution 3.3

// Analog input Pin of your board
#define pin 32

//MQ135
#define type "MQ-135"

// For Arduino UNO/MEGA/NANO
#define ADC_Bit_Resolution 10

//RS / R0 = 3.6 ppm
#define RatioMQ135CleanAir 3.6

//Declare Sensor
MQUnifiedsensor MQ135(placa, Voltage_Resolution, ADC_Bit_Resolution, pin, type);

WiFiClient wifiClient;
PubSubClient client(wifiClient);

void setup_wifi()
{
  WiFi.begin(ssid, pass);

  Serial.print("Connecting to ");
  Serial.println(ssid);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  Serial.print("Connected, IP address: ");
  Serial.println(WiFi.localIP());
}

void connect_to_broker() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "Mq135";
    clientId += String(random(0xffff), HEX);
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      client.subscribe(MQTT_LDP_TOPIC);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 2 seconds");
      delay(2000);
    }
  }
}

void callback(char* topic, byte *payload, unsigned int length) {
  Serial.println("-------new message from broker-----");
  Serial.print("topic: ");
  Serial.println(topic);
  Serial.print("message: ");
  Serial.write(payload, length);
  Serial.println();
  if (*payload == '1') current_ledState = HIGH;
  if (*payload == '0') current_ledState = LOW;
}

void setup_mq135(){
  //Set math model to calculate the PPM concentration and the value of constants
  MQ135.setRegressionMethod(1); //_PPM =  a*ratio^b

  //Init Sensor
  MQ135.init();
 
  // In this routine the sensor will measure the resistance of the sensor supposing before was pre-heated
  // and now is on clean air (Calibration conditions), and it will setup R0 value.
  // We recomend execute this routine only on setup or on the laboratory and save on the eeprom of your arduino
  // This routine not need to execute to every restart, you can load your R0 if you know the value
  // Verbose PreHeat
  Serial.print("Calibrating ...");

  //MQ CAlibration
  float calcR0 = 0;
  for(int i = 1; i<=10; i ++){
  
  // Update data, the arduino will be read the voltage on the analog pin
  MQ135.update();
  calcR0 += MQ135.calibrate(RatioMQ135CleanAir);
  MQ135.setR0(calcR0/10);

  // End Calibration
  }

  // Verobose Done
  Serial.print("Calibration Done.");
  
  if(isinf(calcR0)) {
    Serial.println("Warning: Conection Issue Founded, R0 is infite : Open Circuit Detected"); while(1);
    }
  if(calcR0 == 0){
    Serial.println("Warning: Conection Issue Founded, R0 is zero : Analog Pin Short Circuit Ground"); while(1);
    }

  // Debug Mode
  //MQ135.serialDebug(false);
}

void send_data() {
  // Update data, the esp will be read the voltage on the analog pin
  MQ135.update();

  // Configurate PPM ecuation CO concentration
  MQ135.setA(605.18); MQ135.setB(-3.937);
  float CO = MQ135.readSensor();
  
  // Configurate PPM ecuation CO2 concentration
  MQ135.setA(110.47); MQ135.setB(-2.862);
  float CO2 = MQ135.readSensor();
  
  // Configurate PPM ecuation Alcohol concentration
  MQ135.setA(77.255); MQ135.setB(-3.18);
  float Alcohol = MQ135.readSensor();
  
  // Configurate PPM ecuation Toluene concentration
  MQ135.setA(44.947); MQ135.setB(-3.445);
  float Toluene = MQ135.readSensor();
  
  // Configurate PPM ecuation NH4 concentration
  MQ135.setA(102.2); MQ135.setB(-2.473);
  float NH4 = MQ135.readSensor();

  // Configurate PPM ecuation Acetone concentration
  MQ135.setA(34.668); MQ135.setB(-3.369);
  float Acetone = MQ135.readSensor();

//fix here
  client.publish(MQTT_LDP_TOPIC, "mq135");
  delay(2000); 
  client.publish(MQTT_LDP_TOPIC, Sensor_id);
  delay(2000);  
  
  char temp[100];
  char msg[1000];
  char comma[2] = ",";
  sprintf(temp, "%f",CO);
  char co[4] = "CO:";
  // strcat(co, temp);
  client.publish(MQTT_LDP_TOPIC, temp);
  delay(2000);
  sprintf(temp, "%f",CO2);
  char co2[5] = "CO2:";
  // strcat(co2, temp);
  client.publish(MQTT_LDP_TOPIC, temp);
  delay(2000);

  sprintf(temp, "%f",Acetone);
  char acetone[9] = "Acetone:";
  client.publish(MQTT_LDP_TOPIC, temp);
  delay(2000);

  sprintf(temp, "%f",NH4);
  char nh4[5] = "NH4:";
  // strcat(nh4, temp);
  client.publish(MQTT_LDP_TOPIC, temp);
  delay(2000);

  sprintf(temp, "%f",Alcohol);
  char alcohol[9] = "Alcohol:";
  // strcat(alcohol, temp);
  client.publish(MQTT_LDP_TOPIC, temp);
  delay(2000);

  sprintf(temp, "%f",Toluene);
  char toluene[9] = "Toluene:";
  // strcat(toluene, temp);
  client.publish(MQTT_LDP_TOPIC, temp);
  delay(2000);
  // strcat(acetone, temp);
}

void setup(){
  Serial.begin(115200);
  Serial.setTimeout(500);
  setup_wifi();
  setup_mq135();
  client.setServer(MQTT_SERVER, MQTT_PORT );
  client.setCallback(callback);
  connect_to_broker();
}
void loop()
{
  client.loop();
  if (!client.connected()) {
    connect_to_broker();
  }
  if (last_ledState != current_ledState) {
    last_ledState = current_ledState;
    digitalWrite(22, current_ledState);
    Serial.println(current_ledState);
  }
  send_data();
}