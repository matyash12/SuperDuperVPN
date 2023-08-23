from django import forms
from django.forms import ModelForm
from .models import WireGuardInterface, WireGuardPeer, Settings

class WireGuardInterfaceForm(ModelForm):
    class Meta:
        model = WireGuardInterface
        fields = ['Address','SaveConfig','ListenPort','PrivateKey','PublicKey']

class WireGuardPeerForm(ModelForm):
    class Meta:
        model = WireGuardPeer
        fields = ['PublicKey','AllowedIPs']

class SettingsForm(ModelForm):
    class Meta:
        model = Settings
        fields = ['ServerIpAddress']
        labels = {
            'ServerIpAddress':'IP address of this server'
        }