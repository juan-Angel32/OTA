from ota import OTAUpdater
from WIFI_CONFIG import , PASSWORD

firmware_url = "https://github.com/kevinmcaleer/ota_test/main/"

ota_updater = OTAUpdater(WorkStation1, tacho1105, firmware_url, "test_ota.py")

ota_updater.download_and_install_update_if_available()