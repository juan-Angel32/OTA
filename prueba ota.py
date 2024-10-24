from ota import OTAUpdater
from WIFI_CONFIG import SSID, PASSWORD  # Asegúrate de que el archivo tenga estas variables correctamente definidas.

# URL del repositorio de firmware
firmware_url = "https://github.com/juan-Angel32/prueba ota/main/"

# Configuración de la actualización OTA
ota_updater = OTAUpdater(SSID, PASSWORD, firmware_url, "prueba ota.py")

# Descargar e instalar actualización si está disponible
ota_updater.download_and_install_update_if_available()
