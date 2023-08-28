from celery import shared_task
import time
from .models import WireGuardInterface, WireGuardPeer
from . import Wireguard
from django.conf import settings
import os


@shared_task
def HelloWorld():
    time.sleep(5)
    print('HELLO WORLD!')

@shared_task
def Wireguard_from_database_to_config_file():
    wireguard = Wireguard.ConfigFile(settings.WIREGUARD_CONF_FILE_PATH)


    interface = WireGuardInterface.objects.last()
    if interface == None:
        interface = WireGuardInterface()

    peers = []

    for peer in WireGuardPeer.objects.all():
        peers.append({
            'PublicKey':peer.PublicKey,
            'AllowedIPs':peer.AllowedIPs
        })

    wireguard.set_config({
        'Interface':{
            'Address':interface.Address,
            'SaveConfig':interface.SaveConfig,
            'ListenPort':interface.ListenPort,
            'PrivateKey':interface.PrivateKey
        },
        'Peers':peers,
        #for settings extra rules after interface
        'UFW':settings.WIREGUARD_CONFIG_FILE_AFTER_INTERFACE, 
    })
@shared_task
def Restart_wireguard():
    exec(settings.WIREGUARD_COMMAND_TO_RESTART) #TODO some more general way

    

#for deleting config files in templatets/generated_files and qrcodes
@shared_task
def Delete_File(file_path, sleep=0):
    if sleep != 0:
        time.sleep(sleep)
    if os.path.exists(file_path):    
        os.remove(file_path)
    

#deletes everything apart from .gitkeep from generated_files and generated_qr_codes
@shared_task
def CleanGenerated():
    

    #generated_files
    folder_path = settings.CLIENT_CONFIG_FILE_FOLDER
    generated_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]


    for file_path in generated_files:
       Delete_File.delay(file_path)


    #generated_qr_codes
    folder_path = settings.CLIENT_CONFIG_FILE_FOLDER_QR_CODE
    generated_qr_codes = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    for file_path in generated_qr_codes:
       Delete_File.delay(file_path)


    

    



