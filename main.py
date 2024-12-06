# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
import machine
import time
from umail import SMTP
import network
import json
from umqtt.simple import MQTTClient
from ota import OTAUpdater


# Parámetros de configuración
ssid = "WorkStation1"
contraseña_wifi = "tacho11056"

MQTT_SERVER = "62.146.181.199"
MQTT_PORT = "1883"
MQTT_TOPIC = "Bacoon"
MQTT_CLIENT_ID = "esp32"

correo_remitente = "becerrillealjuanangel@gmail.com"
contrasena_remitente = "ofqm urif typx sznd"
correo_destinatario = "122043975@upq.edu.mx"
asunto = "Notificación ESP32-pruebas"
estado = "Activado"
tiempo_deep_sleep = 60 * 1000  # 1 minuto en milisegundos


# Función para conectar a la red WiFi
def conectar_wifi(ssid, contraseña):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print(f"Conectando a la red '{ssid}'...")
        wlan.connect(ssid, contraseña)
        start_time = time.time()

        while not wlan.isconnected():
            if time.time() - start_time > 10:
                print("No se pudo conectar a la red WiFi.")
                return None
            time.sleep(1)

    print("Conexión exitosa!")
    print("Datos de conexión (IP/netmask/gw/DNS):", wlan.ifconfig())
    return wlan

# Función para obtener la dirección MAC del ESP32
def obtener_mac(wlan):
    mac = wlan.config('mac')
    mac_str = ':'.join(f'{b:02X}' for b in mac)
    print(f"Dirección MAC: {mac_str}")
    return mac_str


def obtener_ip():
    ip = red.ifconfig()[0]
    return ip


# Función para configurar el cliente MQTT
def configurar_mqtt(mqtt_server, mqtt_port, client_id):
    client = MQTTClient(client_id, mqtt_server, port=int(mqtt_port))
    try:
        client.connect()
        print("Conectado al servidor MQTT")
    except Exception as e:
        print(f"Error al conectar al servidor MQTT: {e}")
        return None
    return client

# Función para enviar datos por MQTT en formato JSON
def enviar_datos_mqtt(client, topic, mac, ip, estado):
    data = {
        "Identificador": "esp32-pruebas",
        "IP": ip,
        "Estado": estado
    }
    json_data = json.dumps(data)
    client.publish(topic, json_data)
    print(f"Datos enviados: {json_data}")

# Función para enviar correo electrónico
def enviar_correo_con_reintento(remitente, contrasena, destinatario, asunto, mensaje, intentos=10):
    for intento in range(intentos):
        try:
            smtp = SMTP('smtp.gmail.com', 465, ssl=True)
            smtp.login(remitente, contrasena)
            smtp.to(destinatario)
            smtp.write(f"Subject: {asunto}\n")
            smtp.write(f"{mensaje}\n")
            smtp.send()
            smtp.quit()
            print("Correo enviado con éxito!")
            return True
        except Exception as e:
            print(f"Error al enviar el correo (intento {intento + 1} de {intentos}): {e}")
            if intento < intentos - 1:
                print("Reintentando en 5 segundos...")
                time.sleep(5)
    print("No se pudo enviar el correo después de varios intentos.")
    return False

# Configurar deep sleep con RTC para despertar después de un tiempo
def entrar_en_deep_sleep(tiempo_ms):
    print(f"Entrando en deep sleep por {tiempo_ms / 1000} segundos...")
    machine.deepsleep(tiempo_ms)


def detectar_sleep():
# Detectar si el ESP32 está despertando de deep sleep
    if machine.reset_cause() == machine.DEEPSLEEP_RESET:
        print("Despertando del modo deep sleep.")
    else:
        print("Inicio desde un reinicio o encendido.")

def ota():
# Inicializar el OTA Updater
    firmware_url = "https://raw.githubusercontent.com/juan-Angel32/OTA/main/"
    filename = "prueba ota.py"
    ota_updater = OTAUpdater(ssid, contraseña_wifi, firmware_url, filename)

# Procesos principales
def ejecutar_procesos():
    red = conectar_wifi(ssid, contraseña_wifi)
    if red:
        mac_str = obtener_mac(red)
        ip = red.ifconfig()[0]

        client = configurar_mqtt(MQTT_SERVER, MQTT_PORT, MQTT_CLIENT_ID)
        if client:
            enviar_datos_mqtt(client, MQTT_TOPIC, mac_str, ip, estado)

            mensaje_correo = f"El dispositivo con MAC '{mac_str}' sigue en línea. Su IP es {ip}."
            enviar_correo_con_reintento(correo_remitente, contrasena_remitente, correo_destinatario, asunto, mensaje_correo)

        # Desconectar WiFi para ahorrar energía
        red.active(False)

    # Entrar en deep sleep por 1 minuto
    entrar_en_deep_sleep(tiempo_deep_sleep)

# Ejecutar los procesos
ejecutar_procesos()

while True:
    conectar_wifi(ssid, contraseña_wifi)
    MAC=obtener_mac(wlan)
    IP=obtener_ip()
    configurar_mqtt(MQTT_SERVER, MQTT_PORT, MQTT_CLIENT_ID)
    enviar_datos_mqtt(client,MQTT_TOPIC, MAC, IP, estado)
    entrar_en_deep_sleep(tiempo_deep_sleep)
    machiene.reset()
