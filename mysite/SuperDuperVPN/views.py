from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.http import HttpResponse
from . import Wireguard
from .forms import *
from .models import *
from .tasks import *
from django.conf import settings
import os
from wsgiref.util import FileWrapper
import uuid
import qrcode
import qrcode.image.svg
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
import socket


@login_required
def index(request):
    context = {}
    
    context['client_api'] = get_client_ip(request)
    
    peer = WireGuardPeer.objects.filter(Address=get_client_ip(request)+'/32')
    if len(peer) == 0:
        #unsecured connection
        context['connection_is_secured'] = False
    else:
        #secured connection
        context['connection_is_secured'] = True
    
    context['number_of_peers'] = len(WireGuardPeer.objects.all())
    
    max_epoch_time = PeerUsageData.objects.aggregate(Max('epoch_time'))['epoch_time__max']
    
    context['last_wireguard_wg'] = datetime.fromtimestamp(max_epoch_time).strftime('%c')
    
    Transfer_Received_MiB = 0
    Transfer_Sent_MiB = 0
    for peer in PeerUsageData.objects.filter(epoch_time=max_epoch_time):
        Transfer_Received_MiB += peer.Transfer_Received_MiB
        Transfer_Sent_MiB += peer.Transfer_Sent_MiB
        
        
    context['Transfer_Received_MiB'] = Transfer_Received_MiB
    context['Transfer_Sent_MiB'] = Transfer_Sent_MiB
    
    context['server_domain'] = Settings.objects.last().ServerIpAddress
    context['server_ip'] = socket.gethostbyname(Settings.objects.last().ServerIpAddress)
    
    context['git_describe_version'] = get_git_describe()
    context['git_branch_name'] = get_git_branch_name()
    
    context['server_time_and_date'] = datetime.fromtimestamp(time.time()).strftime('%c')
    
    return render(request, "index.html",context)


# i have no idea what this is? wtf
# def view(request):
#    return render(request, "view.html")


@login_required
def edit_interface(request):
    if request.method == "POST":
        instance = WireGuardInterface.objects.last()
        if instance == None:
            instance = WireGuardInterface()

        if "save" in request.POST["action"]:
            # save the interface settings
            form = WireGuardInterfaceForm(request.POST, instance=instance)
            if form.is_valid():
                # Process the form data
                form.save()
                Wireguard_from_database_to_config_file.delay()
                # Do something with the data, e.g., save to a model or send an email
                return redirect(index)
        elif "generate" in request.POST["action"]:
            # generate keys
            #TODO secure it so it wont be accidentaly clicked on
            keymanager = Wireguard.KeyManager()
            private_key_bytes = keymanager.generate_private_key_bytes()
            form = WireGuardInterfaceForm(
                instance=WireGuardInterface(),
                initial={
                    "Address": request.POST["Address"],
                    "ListenPort": request.POST["ListenPort"],
                    "PrivateKey": keymanager.decode_to_utf8(private_key_bytes),
                    "PublicKey": keymanager.decode_to_utf8(
                        keymanager.generate_public_key_bytes(private_key_bytes)
                    ),
                    "PreSharedKey":keymanager.decode_to_utf8(keymanager.generate_preshared_key_bytes())
                },
            )

    else:
        data = WireGuardInterface.objects.last()

        if data == None:
            data = WireGuardInterface()

        form = WireGuardInterfaceForm(instance=data)

    return render(request, "edit_interface.html", {"form": form})


@login_required
def peers(request):
    objects = WireGuardPeer.objects.all()

    objs = []
    for obj in objects:
        peer = {
            'pk':obj.pk,
            'Name':obj.Name,
            'PublicKey':obj.PublicKey,
        }
        #usage data
        usage_data = PeerUsageData.objects.filter(peer_public_key=obj.PublicKey.replace("\n", "")).order_by('-epoch_time').first()
        if usage_data is not None:
            peer['Endpoint'] = usage_data.Endpoint
            peer['Received'] = str(usage_data.Transfer_Received_MiB) + ' MiB' 
            peer['Sent'] = str(usage_data.Transfer_Sent_MiB) + ' MiB'
    


        objs.append(peer)

    return render(request, "peers.html", {"peers": objs})


@login_required
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


@login_required
def delete_peer(request,peer_id):
    peer = get_object_or_404(WireGuardPeer, pk=peer_id)
    peer.delete()
    Wireguard_from_database_to_config_file.delay()
    return redirect('peers')


# make it safer...
# so user can only download those he generated
# TODO user should be able to see only those he generated
@login_required
def qr_code_viewer(request, name_of_the_file):
    image_path = settings.CLIENT_CONFIG_FILE_FOLDER_QR_CODE + name_of_the_file
    with open(image_path, "rb") as image_file:
        response = HttpResponse(image_file.read(), content_type="image/png")
        #Delete_File.s(image_path).apply_async(countdown=60)
        return response


# make it safer...
# so user can only download those he generated
# TODO user should be able to see only those he generated
@login_required
def download_wireguard_client_config(request, name_of_the_file, client_show_name):
    filepath = settings.CLIENT_CONFIG_FILE_FOLDER + name_of_the_file
    # Open the file and create a file-like object
    with open(filepath, "rb") as file:
        content = FileWrapper(file)  # Use FileWrapper with the file object

        response = HttpResponse(content, content_type="text/plain")
        response["Content-Length"] = os.path.getsize(filepath)
        response["Content-Disposition"] = (
            "attachment; filename=%s" % client_show_name+".conf"
        )
        #Delete_File.s(filepath).apply_async(countdown=60)
        return response


# wireguard_conf_file_path = '/Users/matyas/Documents/GitHub/super-duper-vpn/test.conf'
# wireguard = Wireguard.ConfigFile(wireguard_conf_file_path)


# Simple it should be
# You open this page and it should automaticly save it to database
# No hard things
# no setup by user
@login_required
def peer_detail(request, pk):
    
    
    peer = WireGuardPeer.objects.get(pk=pk)
    if peer.Name == '':
        peer.Name = peer.Name
    
    # creating keys
    keymanager = Wireguard.KeyManager()
    
    
    
    private_key_bytes = keymanager.generate_private_key_bytes()
    # private key client
    if peer.PrivateKey == '':
        peer.PrivateKey = keymanager.decode_to_utf8(private_key_bytes)
        # public key client
        peer.PublicKey = keymanager.decode_to_utf8(
            keymanager.generate_public_key_bytes(private_key_bytes)
        )
        peer.PreSharedKey = WireGuardInterface.objects.last().PreSharedKey
    # find suitable client ip
    if peer.Address == '':
        all_possible_ips = Wireguard.IpManager().GetAllPossibleIPS()
        for ip in all_possible_ips:
            # check if in db already in use
            if len(WireGuardPeer.objects.filter(Address=ip + "/32")) == 0:
                # it's free
                peer.Address = ip + "/32"
                break

    # creating DNS
    if peer.DNS == '':
        peer.DNS = "8.8.8.8"

    if peer.AllowedIPs == '':
        # connections to these ips will go through this vpn
        peer.AllowedIPs = "0.0.0.0/0, ::/0"  # everything

    if peer.Endpoint == '':
        # ip address and port of this server
        peer.Endpoint = (
            Settings.objects.last().ServerIpAddress
            + ":"
            + WireGuardInterface.objects.last().ListenPort
        )

    if peer.KeepAlive == '':
        # PersistentKeepalive
        # dont know if this is neccesary? but many people use it
        peer.KeepAlive = WireGuardPeer.objects.get(pk=pk).KeepAlive

    if peer.ServerPublickey == '':
        # Publickey of server needed for Peer to estabilish connection
        peer.ServerPublickey= WireGuardInterface.objects.last().PublicKey

    config = GenerateConfigFile(peer)
    
    if (peer.QRCodeName == ''):
        peer.QRCodeName = CreateQRConfigFile(config)
    
    if (peer.ConfigFileName == ''):
        peer.ConfigFileName = CreateConfigFile(config)
    
    peer.save()
    
    
    # save peer to server wireguard conf file
    Wireguard_from_database_to_config_file.delay()

    return render(request, "add_peer/peer_detail.html", {
        'peer_name':peer.Name,
        'str_config_file':config,
        'qr_code_file':peer.QRCodeName,
        'download_name_config_file':peer.ConfigFileName,
        'client_show_name':peer.Name+'_wireguard',
                                                      })


@login_required
def server_settings(request):
    context = {}
    if request.method == "POST":
        settings = Settings.objects.last()
        if settings == None:
            settings = Settings()
        form = SettingsForm(request.POST, instance=settings)
        if form.is_valid():
            # Process the form data
            form.save()
            # Do something with the data, e.g., save to a model or send an email
            return redirect(index)
    else:
        data = Settings.objects.last()

        if data == None:
            data = Settings()

        form = SettingsForm(instance=data)
    context["form"] = form
    return render(request, "settings.html", context)


@login_required
def add_peer(request):
    context = {}
    if request.method == "POST":
        if "add" in request.POST["action"]:
            form = WireguardPeerCreateForm(request.POST)
            if form.is_valid():
                obj = form.save()
                return redirect("peer_detail", obj.pk)
    else:
        form = WireguardPeerCreateForm()

    context["form"] = form
    return render(request, "add_peer/add_peer.html", context)


def login_page(request):
    if request.user.is_authenticated:
        return redirect("index")
    context = {}
    context["form"] = LoginForm()
    context["invalid"] = False
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                return redirect("index")
        context["invalid"] = True
        context["form"] = form
    return render(request, "accounts/login.html", context)


def logout_page(request):
    context = {}
    logout(request)
    return render(request, "accounts/logout.html", context)


@login_required
def extras(request):
    context = {}
    return render(request,"extras.html",context)

#extras
@login_required
def extras_delete_generated_files(request):
    context = {}
    CleanGenerated()
    return redirect('extras')

#extras
@login_required
def extras_Load_Host_Wireguard_Logs(request):
    context = {}
    Load_Host_Wireguard_Logs.delay()
    return redirect('extras')

#extras
@login_required
def extras_PeerUsageData(request):
    context = {}
    Calculate_PeerUsageData.delay()
    return redirect('extras')
