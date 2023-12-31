from django import forms
from django.forms import ModelForm
from .models import WireGuardInterface, WireGuardPeer, Settings
from django.core.exceptions import ValidationError
import socket
from . import Wireguard
from .tasks import *

class BulmaTextInput(forms.TextInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({'class': 'input', 'onchange':'set_unsaved_work(true)'})

#the same as BulmaTextInput but with id
class BulmaTextInputAddPeerName(forms.TextInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({'class': 'input', 'onchange':'set_unsaved_work(true)','oninput':'NameChange(); NameChangeNotification()','id':'PeerName'})


class BulmaPasswordInput(forms.PasswordInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({'class': 'input'})

class BulmaIntegerInput(forms.NumberInput):
   def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({'class': 'input'})

#the same as BulmaIntegerInput used for keepalive
class BulmaIntegerInputKeepAlive(forms.NumberInput):
   def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({'class': 'input','id':'keepaliveinput'})




class WireGuardInterfaceForm(ModelForm):
    #generate the keys if empty
    keymanager = Wireguard.KeyManager()
    private_key_bytes = keymanager.generate_private_key_bytes()
    
    
    Address = forms.CharField(widget=BulmaTextInput,label='Address',initial='10.0.0.1/32')
    ListenPort = forms.CharField(widget=BulmaTextInput,label='Listen port',initial='51820')
    PrivateKey = forms.CharField(widget=BulmaTextInput,required=False,label='Private key',initial=keymanager.decode_to_utf8(private_key_bytes))
    PublicKey = forms.CharField(widget=BulmaTextInput,required=False,label='Public key',initial=keymanager.decode_to_utf8(
                        keymanager.generate_public_key_bytes(private_key_bytes)
                    ),)
    PreSharedKey = forms.CharField(widget=BulmaTextInput,required=False,label='PreShared Key',initial=keymanager.decode_to_utf8(keymanager.generate_preshared_key_bytes()))
    class Meta:
        model = WireGuardInterface
        fields = ['Address','ListenPort','PrivateKey','PublicKey','PreSharedKey']


class WireGuardPeerForm(ModelForm):
    Name = forms.CharField(widget=BulmaTextInput,required=True)
    class Meta:
        model = WireGuardPeer
        fields = ['Name']


#used in add_peer
class WireguardPeerCreateForm(ModelForm):
    Name = forms.CharField(widget=BulmaTextInputAddPeerName,required=True, label='Name')
    KeepAlive = forms.IntegerField(widget=BulmaIntegerInputKeepAlive,required=False,label='Keep alive',initial=0,min_value=0)
    DNS = forms.CharField(widget=BulmaTextInput,required=True,label='DNS',initial='8.8.8.8')
    AllowedIPs = forms.CharField(widget=BulmaTextInput,required=True,label='AllowedIPS',initial='0.0.0.0/0, ::/0')
    class Meta:
        model = WireGuardPeer
        fields = ['Name','KeepAlive','DNS','AllowedIPs']
    
    def clean_Name(self):
        data = self.cleaned_data["Name"]
        if WireGuardPeer.objects.filter(Name=data).count() > 0:
            raise ValidationError("This NAME already exist's!")
        return data

class SettingsForm(ModelForm):
    
    
    
    
    ServerIpAddress = forms.CharField(widget=BulmaTextInput,required=True,label='IP address or domain of this server',initial=get_public_ip())
    class Meta:
        model = Settings
        fields = ['ServerIpAddress']

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=200,widget=BulmaTextInput)
    password = forms.CharField(label='Password', widget=BulmaPasswordInput)


    
    