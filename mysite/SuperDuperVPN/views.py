from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.http import HttpResponse
from . import Wireguard
from .forms import WireGuardInterfaceForm, WireGuardPeerForm
from .models import WireGuardInterface, WireGuardPeer
from .tasks import Wireguard_from_database_to_config_file, Restart_wireguard
from django.conf import settings
from django.http import FileResponse
import os
from wsgiref.util import FileWrapper
import uuid
import qrcode
from io import BytesIO
import qrcode.image.svg


def index(request):
    return render(request, "index.html")


def view(request):
    return render(request, "view.html")


def edit_interface(request):
    if request.method == "POST":
        instance = WireGuardInterface.objects.last()
        if instance == None:
            instance = WireGuardInterface()
        form = WireGuardInterfaceForm(request.POST, instance=instance)
        if form.is_valid():
            # Process the form data
            form.save()
            Wireguard_from_database_to_config_file.delay()
            # Do something with the data, e.g., save to a model or send an email
            return redirect(index)
    else:
        data = WireGuardInterface.objects.last()

        if data == None:
            data = WireGuardInterface()

        form = WireGuardInterfaceForm(instance=data)

    return render(request, "edit_interface.html", {"form": form})


def peers(request):
    forms = []
    for peer in WireGuardPeer.objects.all():
        forms.append(peer)
    return render(request, "peers.html", {"forms": forms})


def edit_peer(request, peer_id):
    peer = get_object_or_404(WireGuardPeer, pk=peer_id)
    if request.method == "POST":
        form = WireGuardPeerForm(request.POST, instance=peer)
        if "save" == request.POST["action"]:
            if form.is_valid():
                # Process the form data
                form.save()
                Wireguard_from_database_to_config_file.delay()
                # Do something with the data, e.g., save to a model or send an email
                return redirect(index)
        elif "delete" == request.POST["action"]:
            peer.delete()
            Wireguard_from_database_to_config_file.delay()
            return redirect(index)
    else:
        form = WireGuardPeerForm(instance=peer)

    return render(request, "edit_peer.html", {"form": form})


def add_peer(request):
    context = {
        'download_name_config_file' : 'none',#default value
        'show_download_options':False #whether it should show qr code, download link, private key etc..
    }
    if request.method == "POST":
        if "save" == request.POST["action"]:
            form = WireGuardPeerForm(request.POST, instance=WireGuardPeer())
            if form.is_valid():
                # Process the form data
                form.save()
                Wireguard_from_database_to_config_file.delay()
                # Do something with the data, e.g., save to a model or send an email
                return redirect(index)
        else:
            if "generate" == request.POST["action"]:
                #generates all peers fields
                keymanager = Wireguard.KeyManager()


                #pre-filling form
                private_key_bytes = keymanager.generate_private_key_bytes()

                #trying to get endpoint
                if WireGuardPeer.objects.last() != None:
                    endpoint = WireGuardPeer.objects.last().Endpoint
                else: 
                    endpoint = 'not found'

                #trying to get listening port
                if WireGuardInterface.objects.last() != None:
                    listening_port = WireGuardInterface.objects.last().ListenPort
                else: 
                    listening_port = '51820'
                
                wireguard_peer = {
                    "PublicKey": keymanager.decode_to_utf8(
                            keymanager.generate_public_key_bytes(
                                private_key=private_key_bytes
                            )
                        ),
                        "AllowedIPs": settings.DEFAULT_ALLOWED_IPS,
                        "Endpoint":endpoint+':'+listening_port
                }

                
                context["private_key"] = keymanager.decode_to_utf8(private_key_bytes)
            elif "refresh" == request.POST['action']:
                
                wireguard_peer = {
                    "PublicKey": request.POST['PublicKey'],
                        "AllowedIPs": request.POST['AllowedIPs'],
                        "Endpoint":request.POST['Endpoint']
                }
                #dont make anything new just show updated config file qr code, etc..
                pass
            
            form = WireGuardPeerForm(
                    instance=WireGuardPeer(),
                    initial=wireguard_peer
                )
            #showing addition things to make user interface better
            
            
            #showing config file to copy paste
            config = {}

            #TODO check if the setup is correct
            #interface part
            wireguard_interface = WireGuardInterface.objects.last()
            if wireguard_interface != None:
                config['Interface'] = {
                    'PrivateKey':wireguard_interface.PrivateKey,
                    'ListenPort':wireguard_interface.ListenPort,
                    'Address':wireguard_interface.Address,
                    'DNS':settings.DEFAULT_DNS
                }
            #peers part
            config['Peers'] = [{
                'PublicKey':wireguard_peer['PublicKey'],
                'AllowedIPs':wireguard_peer['AllowedIPs'],
                'Endpoint':wireguard_peer['Endpoint']
            }]
            filename = str(uuid.uuid4()) + '.conf' #unique filename
            filepath = settings.CLIENT_CONFIG_FILE_FOLDER+filename
            wireguard_config_file =  Wireguard.ConfigFile(filepath)
            context['str_config_file'] = wireguard_config_file.create_config_string(config) #showing config file to copy paste

            #creating download file for client
            wireguard_config_file.set_config(config)
            print('Wireguard config file generated:',filepath)
            context['download_name_config_file'] = filename

            

            #qr code generation
            qr_code = qrcode.make(context['str_config_file'])
            filename = str(uuid.uuid4())+'.png'
            qr_code_save_path = settings.CLIENT_CONFIG_FILE_FOLDER_QR_CODE+filename
            qr_code.save(qr_code_save_path) #saving qr code
            context['qr_code_file'] = filename


            context['show_download_options'] = True #we want to give user a option to get his config file


    else:
        form = WireGuardPeerForm(instance=WireGuardPeer())
    context["form"] = form
    return render(request, "add_peer.html", context)
#make it safer...
#so user can only download those he generated
#TODO user should be able to see only those he generated
def qr_code_viewer(request,name_of_the_file):
    image_path = settings.CLIENT_CONFIG_FILE_FOLDER_QR_CODE+ name_of_the_file
    with open(image_path, 'rb') as image_file:
        response = HttpResponse(image_file.read(), content_type='image/png')
        return response
#make it safer...
#so user can only download those he generated
#TODO user should be able to see only those he generated
def download_wireguard_client_config(request,name_of_the_file):
    filename = settings.CLIENT_CONFIG_FILE_FOLDER + name_of_the_file

    # Open the file and create a file-like object
    with open(filename, 'rb') as file:
        content = FileWrapper(file)  # Use FileWrapper with the file object

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Length'] = os.path.getsize(filename)
        response['Content-Disposition'] = 'attachment; filename=%s' % 'wireguard_client_config_file.conf'
        return response

def restart_wireguard(request):
    if request.method == "POST":
        # restart wireguard
        Restart_wireguard.delay()
        return redirect(index)
    return render(request, "restart_wireguard.html", {})


# wireguard_conf_file_path = '/Users/matyas/Documents/GitHub/super-duper-vpn/test.conf'
# wireguard = Wireguard.ConfigFile(wireguard_conf_file_path)
