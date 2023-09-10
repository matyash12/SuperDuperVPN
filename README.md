# Wireguard GUI
A GUI to manage your Wireguard setup.

## Features
* Add, Edit, Delete peers (clients)
* Create, Edit wg0.conf
* See each peer usage (like command "wg")
* User managment using Django

# Install guide

1. Have somewhere to run. Like Kamatera. Tested on Ubuntu 22.04.3 LTS
2. Install Wireguard [Installation guide](https://www.wireguard.com/install/)
3. Install Docker [Installation guide](https://docs.docker.com/engine/install/ubuntu/)
4. `git pull`
5. Create folder for WireGuard Logs in "/etc/wireguard/wireguard_logs"
6. In /SuperDuperVPN/host_scripts run `chmod +x run.sh apply_wireguard_conf.sh wireguard_logs.sh`
7. Run crontab -e and add  `* * * * * /SuperDuperVPN/host_scripts/run.sh`
8. In /SuperDuperVPN/mysite/mysite/ copy settings_example.py settings.py and change CSRF_TRUSTED_ORIGINS and SECRET_KEY
9. Copy rename.env to .env and edit values
10. Copy /SuperDuperVPN/docker/nginx/conf_example.conf to /SuperDuperVPN/docker/nginx/conf.conf and edit it accordingly 
11. Run using `docker compose --build -d`

# Tech stack
* Django
* Docker
* Celery
* Bulma
* Mysql
* Python


# Images
![Image](https://github.com/matyash12/SuperDuperVPN/blob/50857e2956be706fee68cdeb7e5424d93093fe30/readme_images/index.png)
![Image](https://github.com/matyash12/SuperDuperVPN/blob/50857e2956be706fee68cdeb7e5424d93093fe30/readme_images/peer_view.png)
![Image](https://github.com/matyash12/SuperDuperVPN/blob/50857e2956be706fee68cdeb7e5424d93093fe30/readme_images/peers_list.png)
![Image](https://github.com/matyash12/SuperDuperVPN/blob/50857e2956be706fee68cdeb7e5424d93093fe30/readme_images/login.png)
