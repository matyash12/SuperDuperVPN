from django import forms
from django.forms import ModelForm
from .models import WireGuardInterface, WireGuardPeer, Settings


class BulmaTextInput(forms.TextInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({'class': 'input'})

class BulmaPasswordInput(forms.PasswordInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({'class': 'input'})

class BulmaIntegerInput(forms.NumberInput):
   def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({'class': 'input'})



class WireGuardInterfaceForm(ModelForm):
    Address = forms.CharField(widget=BulmaTextInput,label='Address')
    ListenPort = forms.CharField(widget=BulmaTextInput,label='Listen port')
    PrivateKey = forms.CharField(widget=BulmaTextInput,required=False,label='Private key')
    PublicKey = forms.CharField(widget=BulmaTextInput,required=False,label='Public key')
     
    class Meta:
        model = WireGuardInterface
        fields = ['Address','ListenPort','PrivateKey','PublicKey']


class WireGuardPeerForm(ModelForm):
    Name = forms.CharField(widget=BulmaTextInput,required=True)
    PublicKey = forms.CharField(widget=BulmaTextInput)
    AllowedIPs = forms.CharField(widget=BulmaTextInput)
    class Meta:
        model = WireGuardPeer
        fields = ['Name','PublicKey','AllowedIPs']


#used in add_peer_name
class WireguardPeerNameForm(ModelForm):
    Name = forms.CharField(widget=BulmaTextInput,required=True, label='Name')
    KeepAlive = forms.IntegerField(widget=BulmaIntegerInput,required=True,label='Keep alive',help_text='0 = means disable')
    class Meta:
        model = WireGuardPeer
        fields = ['Name','KeepAlive']

class SettingsForm(ModelForm):
    ServerIpAddress = forms.CharField(widget=BulmaTextInput,required=True,label='IP address or domain of this server')
    class Meta:
        model = Settings
        fields = ['ServerIpAddress']

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=200,widget=BulmaTextInput)
    password = forms.CharField(label='Password', widget=BulmaPasswordInput)
