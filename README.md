# super-duper-vpn
Great easy-to-use VPN for safe connection!

# Wireguard Config file
[Interface]
Address = 
SaveConfig = 
ListenPort = 
PrivateKey = 

[Peer]
Address =
AllowedIPs =
Endpoint =


# How to install
chmod +x run.sh apply_wireguard_conf.sh wireguard_logs.sh


# How to update
git pull
docker volume rm superdupervpn_my_shared_volume
docker compose up django celery -d --build