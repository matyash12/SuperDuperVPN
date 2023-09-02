from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.http import HttpResponse
from . import Wireguard
from .forms import (
    WireGuardInterfaceForm,
    WireGuardPeerForm,
    SettingsForm,
    WireguardPeerNameForm,
    LoginForm
)
from .models import WireGuardInterface, WireGuardPeer, Settings, PeerUsageData
from .tasks import Wireguard_from_database_to_config_file, Restart_wireguard, Delete_File,CleanGenerated,Load_Host_Wireguard_Logs,Calculate_PeerUsageData
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


@login_required
def index(request):
    return render(request, "index.html")


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
            # generate private key
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


# make it safer...
# so user can only download those he generated
# TODO user should be able to see only those he generated
@login_required
def qr_code_viewer(request, name_of_the_file):
    image_path = settings.CLIENT_CONFIG_FILE_FOLDER_QR_CODE + name_of_the_file
    with open(image_path, "rb") as image_file:
        response = HttpResponse(image_file.read(), content_type="image/png")
        Delete_File.s(image_path).apply_async(countdown=60)
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
        Delete_File.s(filepath).apply_async(countdown=60)
        return response


# wireguard_conf_file_path = '/Users/matyas/Documents/GitHub/super-duper-vpn/test.conf'
# wireguard = Wireguard.ConfigFile(wireguard_conf_file_path)


# Simple it should be
# You open this page and it should automaticly save it to database
# No hard things
# no setup by user
@login_required
def add_peer(request, pk):
    context = {}
    data = {}  # all things needed to make config file for client
    # creating keys
    keymanager = Wireguard.KeyManager()
    private_key_bytes = keymanager.generate_private_key_bytes()
    # private key client
    data["PrivateKey"] = keymanager.decode_to_utf8(private_key_bytes)
    # public key client
    data["PublicKey"] = keymanager.decode_to_utf8(
        keymanager.generate_public_key_bytes(private_key_bytes)
    )
    # find suitable client ip
    all_possible_ips = Wireguard.IpManager().GetAllPossibleIPS()
    for ip in all_possible_ips:
        # check if in db already in use
        if len(WireGuardPeer.objects.filter(AllowedIPs=ip + "/32")) == 0:
            # it's free
            data["Address"] = ip + "/32"
            break

    # creating DNS
    data["DNS"] = "8.8.8.8"

    # connections to these ips will go through this vpn
    data["AllowedIPs"] = "0.0.0.0/0, ::/0"  # everything

    # ip address and port of this server
    data["Endpoint"] = (
        Settings.objects.last().ServerIpAddress
        + ":"
        + WireGuardInterface.objects.last().ListenPort
    )

    # PersistentKeepalive
    # dont know if this is neccesary? but many people use it
    data["PersistentKeepalive"] = 30

    # Publickey of server needed for Peer to estabilish connection
    data["ServerPublickey"] = WireGuardInterface.objects.last().PublicKey

    # This what client needs to add to his local wireguard.
    client_config_wireguard = {
        "Interface": {
            "PrivateKey": data["PrivateKey"],
            "Address": data["Address"],
            "DNS": data["DNS"],
        },
        "Peers": [
            {
                "PublicKey": data["ServerPublickey"],
                "AllowedIPs": data["AllowedIPs"],
                "Endpoint": data["Endpoint"],
                "PersistentKeepalive": data["PersistentKeepalive"],
            }
        ],
    }

    # add to database this peer(client)
    peer = WireGuardPeer.objects.get(pk=pk)
    context["peer_name"] = peer.Name
    peer.PublicKey = data["PublicKey"]
    peer.AllowedIPs = data["Address"]
    peer.Endpoint = ""
    peer.save()
    # save peer to server wireguard conf file
    Wireguard_from_database_to_config_file.delay()

    # creating config file
    filename = str(uuid.uuid4()) + ".conf"  # unique filename
    filepath = settings.CLIENT_CONFIG_FILE_FOLDER + filename
    Delete_File.s(filepath).apply_async(countdown=300)
    wireguard_config_file = Wireguard.ConfigFile(filepath)
    # showing config file to copy paste
    context["str_config_file"] = wireguard_config_file.create_config_string(
        client_config_wireguard
    )

    # creating download file for client
    wireguard_config_file.set_config(client_config_wireguard)
    print("Wireguard config file generated:", filepath)
    context["download_name_config_file"] = filename

    # qr code generation #TODO maybe run this in background..
    qr = qrcode.QRCode(
        version=3,  # Specify the version here
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        border=0,
    )
    qr.add_data(context["str_config_file"])
    qr.make(fit=True)
    qr_code = qr.make_image(fill_color="black", back_color="white")
    filename = str(uuid.uuid4()) + ".png"
    qr_code_save_path = settings.CLIENT_CONFIG_FILE_FOLDER_QR_CODE + filename
    qr_code.save(qr_code_save_path)  # saving qr code
    Delete_File.s(qr_code_save_path).apply_async(countdown=300)
    context["qr_code_file"] = filename

    #this is what the file will be named when user download
    context["client_show_name"] = context["peer_name"] + "_wireguard"

    return render(request, "add_peer/add_peer.html", context)


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
def add_peer_name(request):
    context = {}
    if request.method == "POST":
        if "add" in request.POST["action"]:
            form = WireguardPeerNameForm(request.POST)
            if form.is_valid():
                obj = form.save()
                return redirect("add_peer", obj.pk)
    else:
        form = WireguardPeerNameForm()

    context["form"] = form
    return render(request, "add_peer/add_peer_name.html", context)


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