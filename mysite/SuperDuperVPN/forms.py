from django import forms
from django.forms import ModelForm
from .models import WireGuardInterface, WireGuardPeer, Settings

class WireGuardInterfaceForm(ModelForm):
    class Meta:
        model = WireGuardInterface
        fields = ['Address','SaveConfig','ListenPort','PrivateKey','PublicKey']


class WireGuardPeerForm(ModelForm):
    Name = forms.CharField(required=True)
    class Meta:
        model = WireGuardPeer
        fields = ['Name','PublicKey','AllowedIPs']

class WireguardPeerNameForm(ModelForm):
    Name = forms.CharField(required=True)
    class Meta:
        model = WireGuardPeer
        fields = ['Name']

class SettingsForm(ModelForm):
    class Meta:
        model = Settings
        fields = ['ServerIpAddress']
        labels = {
            'ServerIpAddress':'IP address of this server'
        }