from celery import shared_task
import time
from .models import WireGuardInterface, WireGuardPeer
from . import Wireguard
from django.conf import settings
import subprocess

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
            'AllowedIPs':peer.AllowedIPs,
            'Endpoint':peer.Endpoint
        })

    wireguard.set_config({
        'Interface':{
            'Address':interface.Address,
            'SaveConfig':interface.SaveConfig,
            'ListenPort':interface.ListenPort,
            'PrivateKey':interface.PrivateKey
        },
        'Peers':peers
    })
@shared_task
def Restart_wireguard():
    exec(settings.WIREGUARD_COMMAND_TO_RESTART) #TODO some more general way

    
