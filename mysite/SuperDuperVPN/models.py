from django.db import models

# Create your models here.
class WireGuardConfigFile(models.Model):
    Type = models.CharField(max_length=200)
    #Interface
    Address = models.CharField(max_length=200)
    SaveConfig = models.CharField(max_length=200)
    ListenPort = models.CharField(max_length=200)
    PrivateKey = models.CharField(max_length=200)
    #Peer
    PublicKey = models.CharField(max_length=200)
    AllowedIPs = models.CharField(max_length=200)
    Endpoint = models.CharField(max_length=200)

class WireGuardInterface(models.Model):
    Address = models.CharField(max_length=200,default='10.8.0.1/24')
    SaveConfig = models.CharField(max_length=200, default='true')
    ListenPort = models.CharField(max_length=200,default='51820')
    PrivateKey = models.CharField(max_length=200)
    #not needed for interface but needed for peers
    PublicKey = models.CharField(max_length=200)

class WireGuardPeer(models.Model):
    #client gives this name it is for to friendly-know what is it
    Name = models.CharField(max_length=200)
    PublicKey = models.CharField(max_length=200)
    AllowedIPs = models.CharField(max_length=200)
    Endpoint = models.CharField(max_length=200)

class Settings(models.Model):
    ServerIpAddress = models.CharField(max_length=200)