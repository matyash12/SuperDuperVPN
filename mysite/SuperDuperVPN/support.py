#For background script which arent really visible
#TODO: implement redis and ..
from .models import WireGuardInterface
from . import Wireguard

def Wireguard_from_database_to_config_file():
    wireguard_conf_file_path = '/Users/matyas/Documents/GitHub/super-duper-vpn/test.conf'


    interface = WireGuardInterface.objects.last()
    if interface == None:
        interface = WireGuardInterface()

    print(interface)
    wireguard = Wireguard.ConfigFile(wireguard_conf_file_path)

Wireguard_from_database_to_config_file()