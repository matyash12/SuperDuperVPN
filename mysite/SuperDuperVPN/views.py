from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.http import HttpResponse
from . import Wireguard
from .forms import WireGuardInterfaceForm, WireGuardPeerForm, SettingsForm, WireguardPeerNameForm
from .models import WireGuardInterface, WireGuardPeer, Settings
from .tasks import Wireguard_from_database_to_config_file, Restart_wireguard
from django.conf import settings
import os
from wsgiref.util import FileWrapper
import uuid
import qrcode
import qrcode.image.svg
from django.core.paginator import Paginator

def index(request):
    return render(request, "index.html")


def view(request):
    return render(request, "view.html")


def edit_interface(request):
    if request.method == "POST":
        instance = WireGuardInterface.objects.last()
        if instance == None:
            instance = WireGuardInterface()
        
        if 'save' in request.POST['action']:
            #save the interface settings
            form = WireGuardInterfaceForm(request.POST, instance=instance)
            if form.is_valid():
                # Process the form data
                form.save()
                Wireguard_from_database_to_config_file.delay()
                # Do something with the data, e.g., save to a model or send an email
                return redirect(index)
        elif 'generate' in request.POST['action']:
            #generate private key
            keymanager = Wireguard.KeyManager()
            private_key_bytes = keymanager.generate_private_key_bytes()
            form = WireGuardInterfaceForm(instance=WireGuardInterface(), initial={
                'Address':request.POST['Address'],
                'SaveConfig':request.POST['SaveConfig'],
                'ListenPort':request.POST['ListenPort'],
                'PrivateKey':keymanager.decode_to_utf8(private_key_bytes),
                'PublicKey':keymanager.decode_to_utf8(keymanager.generate_public_key_bytes(private_key_bytes))
            })

    else:
        data = WireGuardInterface.objects.last()

        if data == None:
            data = WireGuardInterface()

        form = WireGuardInterfaceForm(instance=data)

    return render(request, "edit_interface.html", {"form": form})


def peers(request):
    objects = WireGuardPeer.objects.all()
    for obj in objects:
        obj.PublicKey = obj.PublicKey[:10]
    paginator = Paginator(objects, 10)  # Show 10 objects per page
    
    page = request.GET.get('page')
    objects_page = paginator.get_page(page)

    return render(request, 'peers.html', {'peers': objects_page})


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





# wireguard_conf_file_path = '/Users/matyas/Documents/GitHub/super-duper-vpn/test.conf'
# wireguard = Wireguard.ConfigFile(wireguard_conf_file_path)


#Simple it should be
#You open this page and it should automaticly save it to database
#No hard things
#no setup by user
def add_peer(request,pk):
    context = {}
    data = {} #all things needed to make config file for client
    #creating keys
    keymanager = Wireguard.KeyManager()
    private_key_bytes = keymanager.generate_private_key_bytes()
    #private key client
    data["PrivateKey"] = keymanager.decode_to_utf8(private_key_bytes)
    #public key client
    data["PublicKey"] = keymanager.decode_to_utf8(keymanager.generate_public_key_bytes(private_key_bytes))
    #find suitable client ip
    all_possible_ips = Wireguard.IpManager().GetAllPossibleIPS()
    for ip in all_possible_ips:
        #check if in db already in use
        if len(WireGuardPeer.objects.filter(AllowedIPs=ip+'/32')) == 0:
            #it's free
            data['Address'] = ip+'/32'
            break

    
    #creating DNS
    data["DNS"] = '8.8.8.8'

    #connections to these ips will go through this vpn
    data["AllowedIPs"] = '0.0.0.0/0, ::/0' #everything

    #ip address and port of this server 
    data["Endpoint"] = Settings.objects.last().ServerIpAddress+':'+WireGuardInterface.objects.last().ListenPort
    
    #PersistentKeepalive
    #dont know if this is neccesary? but many people use it
    data["PersistentKeepalive"] = 30
    
    #Publickey of server needed for Peer to estabilish connection
    data["ServerPublickey"] =  WireGuardInterface.objects.last().PublicKey
    

    #This what client needs to add to his local wireguard.
    client_config_wireguard = {
        'Interface':{
            'PrivateKey':data["PrivateKey"],
            'Address': data["Address"],
            'DNS':data['DNS'],
        },
        'Peers':[{
            'PublicKey':data['ServerPublickey'],
            'AllowedIPs':data['AllowedIPs'],
            'Endpoint':data['Endpoint'],
            'PersistentKeepalive':data['PersistentKeepalive']
        }]
    }

    #add to database this peer(client)
    peer = WireGuardPeer.objects.get(pk=pk)
    context['peer_name'] = peer.Name
    peer.PublicKey = data['PublicKey']
    peer.AllowedIPs = data['Address']
    peer.Endpoint = ''
    peer.save()
    #save peer to server wireguard conf file
    Wireguard_from_database_to_config_file.delay()




    #creating config file
    filename = str(uuid.uuid4()) + '.conf' #unique filename
    filepath = settings.CLIENT_CONFIG_FILE_FOLDER+filename
    wireguard_config_file =  Wireguard.ConfigFile(filepath)
    #showing config file to copy paste
    context['str_config_file'] = wireguard_config_file.create_config_string(client_config_wireguard)

    #creating download file for client
    wireguard_config_file.set_config(client_config_wireguard)
    print('Wireguard config file generated:',filepath)
    context['download_name_config_file'] = filename

    #qr code generation
    qr_code = qrcode.make(context['str_config_file'])
    filename = str(uuid.uuid4())+'.png'
    qr_code_save_path = settings.CLIENT_CONFIG_FILE_FOLDER_QR_CODE+filename
    qr_code.save(qr_code_save_path) #saving qr code
    context['qr_code_file'] = filename

    return render(request, "add_peer/add_peer.html", context)

def server_settings(request):
    context = {}
    if request.method == 'POST':
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
    context['form'] = form
    return render(request, "settings.html", context)


def add_peer_name(request):
    context = {}
    if request.method == 'POST':
        if 'add' in request.POST['action']:
            form = WireguardPeerNameForm(request.POST)
            if form.is_valid():
                obj = form.save()
                return redirect('add_peer', obj.pk)
    else:
        form = WireguardPeerNameForm()

    context['form'] = form
    return render(request, "add_peer/add_peer_name.html",context)