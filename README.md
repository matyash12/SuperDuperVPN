# super-duper-vpn
Great easy-to-use wireguard GUI for simple managment



# How to install
chmod +x run.sh apply_wireguard_conf.sh wireguard_logs.sh


# How to update
git pull
docker volume rm superdupervpn_my_shared_volume
docker compose up django celery -d --build


# Create user account
For first account creation do:
docker ps
get CONTAINER ID of superdupervpn-django
docker exec -it CONTAINER ID bash
python mysite/manage.py createsuperuser
