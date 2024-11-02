from ota import OTAUpdater
from WIFI_CONFIG import SSID, PASSWORD

# URL del repositorio de firmware en GitHub
firmware_url = "https://raw.githubusercontent.com/juan-Angel32/OTA/main"

# Configuración de la actualización OTA
ota_updater = OTAUpdater(SSID, PASSWORD, firmware_url, "main.py")

# Descargar e instalar actualización si está disponible
ota_updater.download_and_install_update_if_available()
