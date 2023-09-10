#For communicationg with wireguard.
#add, edit, remove, get wireguard .conf file
import subprocess


#How to use:
#get_config -> dict
#set_config(dict) -> save

#config = {
# 'Instance':{
# },
#'Peers':[{
# }
# ]
# }

#TODO fix space after each key ending with '='
#get, set wireguard config-file in dictionary
class ConfigFile:
    #TODO rewrite 
    def __init__(self,path_to_config_file:str) -> None:
        self.path = path_to_config_file

    #get configfile in dictionary
    def get_config(self):
        sections = self.read_file(self.path).strip().split('\n\n')
        
        interface_section = None
        peer_sections = []

        for section in sections:
            lines = section.strip().split('\n')
            section_type = lines[0].strip()

            if section_type == '[Interface]':
                interface_section = {}
                for line in lines[1:]:
                    key, value = map(str.strip, line.split(' = '))
                    interface_section[key] = value
            elif section_type == '[Peer]':
                peer_section = {}
                for line in lines[1:]:
                    key, value = map(str.strip, line.split(' = '))
                    peer_section[key] = value
                peer_sections.append(peer_section)
        
        return {
            'Interface' : interface_section,
            'Peers' : peer_sections
        }


    def create_config_string(self,config) -> str:
        interface = config['Interface']
        peers = config['Peers']
        interface_str = "[Interface]\n"
        for key, value in interface.items():
            interface_str += f"{key} = {value}\n"

        #its when its adding to server config file
        #it needs to add extra rules after [Interface]
        if 'UFW' in config:
            interface_str += '\n'+config['UFW']+'\n'
        
        peers_str = ""
        for peer in peers:
            peers_str += "\n[Peer]\n"
            for key, value in peer.items():
                peers_str += f"{key} = {value}\n"
        return interface_str + peers_str
    
    #set configfile as dictionary 
    #default usage
    def set_config(self,config):
        self.save_file(self.path,self.create_config_string(config))

    #should not be called outside class
    def read_file(self,path) -> str:
        file = open(path, "r")
        file_contents = file.read()
        return file_contents
    #should not be called outside class
    def save_file(self,path,data):
        file = open(path,'w')
        file.write(data)
    


#python wrapper for wireguard keys generation and managment.
class KeyManager:
    def __init__(self) -> None:
        pass

    def decode_to_utf8(self,value):
        return value.decode('utf-8')
    
    def generate_private_key_bytes(self):
        # Run the 'wg genkey' command and capture its output
        genkey_process = subprocess.Popen(['wg', 'genkey'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        genkey_output = genkey_process.communicate()[0]
        #removing last character because it is '\n'.
        genkey_output = genkey_output[:-1] 
        return genkey_output
    
    def generate_public_key_bytes(self,private_key):
        # Run the 'wg pubkey' command and pass the output of 'wg genkey' as input
        pubkey_process = subprocess.Popen(['wg', 'pubkey'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        pubkey_output = pubkey_process.communicate(input=private_key)[0]

        return pubkey_output


    #Call to generate PreSharedKey . Use decode_to_utf8 to convert to string
    def generate_preshared_key_bytes(self) -> bytes:
        genkey_output = subprocess.Popen(['wg', 'genpsk'], stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0]

        genkey_output = genkey_output[:-1]
        return genkey_output

class IpManager:
    def __init__(self) -> None:
        pass
    
    def GetAllPossibleIPS(self):
        base_ip = "10.0.0."
        ips = []

        #ignoring first 5 due to the fact that something may be on them..
        for x in range(5, 256):  # Start from 5 and go up to 255
            ip = base_ip + str(x)
            ips.append(ip)

        return ips