import machine
import time
from umail import SMTP
import network
import json
from umqtt.simple import MQTTClient
from ota import OTAUpdater  # Asegúrate de que la clase OTAUpdater está correctamente implementada

# Función para conectar a la red WiFi
def conectar_wifi(ssid, contraseña):
    wlan = network.WLAN(network.STA_IF)  # Inicializa la interfaz de red WiFi
    wlan.active(True)  # Activa la interfaz de red
    if not wlan.isconnected():  # Verifica si ya está conectado
        print(f"Conectando a la red '{ssid}'...")
        wlan.connect(ssid, contraseña)  # Intenta conectar con la red
        start_time = time.time()  # Marca el tiempo de inicio

        # Espera hasta 10 segundos para conectar
        while not wlan.isconnected():
            if time.time() - start_time > 10:
                print("No se pudo conectar a la red WiFi.")
                return None  # Retorna None si no logra conectar
            time.sleep(1)

    print("Conexión exitosa!")
    print("Datos de conexión (IP/netmask/gw/DNS):", wlan.ifconfig())
    return wlan  # Retorna el objeto de la red si la conexión fue exitosa

# Función para obtener la dirección MAC del ESP32
def obtener_mac(wlan):
    mac = wlan.config('mac')  # Obtiene la MAC en bytes
    mac_str = ':'.join(f'{b:02X}' for b in mac)  # Convertir a formato legible en mayúsculas
    print(f"Dirección MAC: {mac_str}")
    return mac_str

# Función para configurar el cliente MQTT
def configurar_mqtt(mqtt_server, mqtt_port, client_id):
    client = MQTTClient(client_id, mqtt_server, port=int(mqtt_port))
    try:
        client.connect()
        print("Conectado al servidor MQTT")
    except Exception as e:
        print(f"Error al conectar al servidor MQTT: {e}")
        return None  # Retorna None si hay error

    return client

# Función para enviar datos por MQTT en formato JSON
def enviar_datos_mqtt(client, topic, mac, ip, estado):
    data = {
        "Identificador": "esp32",
        "IP": ip,
        "Estado": estado
    }
    json_data = json.dumps(data)
    client.publish(topic, json_data)
    print(f"Datos enviados: {json_data}")

# Función para enviar un correo electrónico
def enviar_correo(remitente, contrasena, destinatario, asunto, mensaje):
    try:
        smtp = SMTP('smtp.gmail.com', 465, ssl=True)  # Conexión SSL a Gmail
        smtp.login(remitente, contrasena)  # Inicio de sesión en el servidor SMTP
        smtp.to(destinatario)  # Especifica el destinatario del correo
        smtp.write(f"Subject: {asunto}\n")  # Añade el asunto del correo
        smtp.write(f"{mensaje}\n")  # Añade el mensaje del correo
        smtp.send()  # Envía el correo
        smtp.quit()  # Cierra la conexión SMTP
        print("Correo enviado con éxito!")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

# Función para configurar el modo de sueño ligero
def entrar_en_light_sleep(tiempo_ms):
    print(f"Entrando en modo light sleep por {tiempo_ms / 1000} segundos...")
    machine.lightsleep(tiempo_ms)

# Parámetros de la red WiFi
ssid = "WorkStation1"
contraseña_wifi = "tacho11056"

# Parámetros del servidor MQTT
MQTT_SERVER = "192.168.137.125"
MQTT_PORT = "1883"
MQTT_TOPIC = "Bacoon"
MQTT_CLIENT_ID = "esp32"

# Parámetros del correo
correo_remitente = "becerrillealjuanangel@gmail.com"
contrasena_remitente = "ofqm urif typx sznd"
correo_destinatario = "122043975@upq.edu.mx"
asunto = "Notificación ESP32"
estado = "Activado"

# Tiempo en milisegundos antes de despertar (e.g., 60 segundos)
tiempo_light_sleep = 60 * 1000  # Convertir a milisegundos

# URL del repositorio OTA (debe terminar en "/")
firmware_url = "https://raw.githubusercontent.com/juan-Angel32/OTA/main/"
filename = "prueba_ota.py"  # Nombre del archivo que deseas actualizar

# Inicializar el OTA Updater
ota_updater = OTAUpdater(ssid, contraseña_wifi, firmware_url, filename)

# Bucle principal
while True:
    # Comprobar y realizar actualizaciones OTA
    ota_updater.download_and_install_update_if_available()
    
    # Conexión a la red WiFi
    red = conectar_wifi(ssid, contraseña_wifi)

    # Si la conexión fue exitosa, enviar los datos por MQTT y correo
    if red:
        # Obtener la dirección MAC del dispositivo
        mac_str = obtener_mac(red)
        ip = red.ifconfig()[0]  # Obtener la IP del dispositivo

        # Configurar el cliente MQTT
        client = configurar_mqtt(MQTT_SERVER, MQTT_PORT, MQTT_CLIENT_ID)
        if client:  # Asegurarse de que el cliente MQTT fue configurado correctamente
            # Enviar los datos por MQTT en formato JSON
            enviar_datos_mqtt(client, MQTT_TOPIC, mac_str, ip, estado)
            
            # Enviar un correo notificando que el ESP32 sigue activo
            mensaje_correo = f"El dispositivo con MAC '{mac_str}' sigue en línea. Su IP es {ip}."
            enviar_correo(correo_remitente, contrasena_remitente, correo_destinatario, asunto, mensaje_correo)
            
            # Desactivar la red después de enviar los datos
            red.active(False)
            
            # Entrar en light sleep por el tiempo especificado antes de repetir el proceso
            entrar_en_light_sleep(tiempo_light_sleep)

    else:
        print("Reintentando conexión en 5 segundos...")
        time.sleep(5)  # Espera antes de volver a intentar conectar
