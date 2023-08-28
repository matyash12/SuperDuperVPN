from django.db import models

# Create your models here.
class WireGuardConfigFile(models.Model):
    Type = models.CharField(max_length=200)
    #Interface
    Address = models.CharField(max_length=200)
    SaveConfig = models.CharField(max_length=200, default='True')
    ListenPort = models.CharField(max_length=200)
    PrivateKey = models.CharField(max_length=200)
    #Peer
    PublicKey = models.CharField(max_length=200)
    AllowedIPs = models.CharField(max_length=200)
    Endpoint = models.CharField(max_length=200)

class WireGuardInterface(models.Model):
    Address = models.CharField(max_length=200,default='10.0.0.1/24')
    SaveConfig = models.CharField(max_length=200, default='True')
    ListenPort = models.CharField(max_length=200,default='51820')
    PrivateKey = models.CharField(max_length=200)
    #not needed for interface but needed for peers
    PublicKey = models.CharField(max_length=200)

class WireGuardPeer(models.Model):
    #client gives this name it is for to friendly-know what is it
    Name = models.CharField(max_length=200, default='NoName')
    PublicKey = models.CharField(max_length=200)
    AllowedIPs = models.CharField(max_length=200)
    Endpoint = models.CharField(max_length=200)

class Settings(models.Model):
    ServerIpAddress = models.CharField(max_length=200)


class WireguardCommandLogs(models.Model):
    epoch_time = models.IntegerField() #time seconds from 1970
    text = models.TextField() #log stored 

#usage data for each peer made from WireguardCommandLogs
#for every second
class PeerUsageData(models.Model):
    epoch_time = models.IntegerField() #time of reading (minute)
    peer_public_key = models.CharField(max_length=200)

    #data from log
    Endpoint = models.CharField(max_length=200)
    AllowedIPs = models.CharField(max_length=200)
    Latest_Handshake = models.IntegerField() #in seconds
    Transfer_Received_MiB = models.IntegerField() #in bytes or bits???
    Transfer_Sent_MiB= models.IntegerField()