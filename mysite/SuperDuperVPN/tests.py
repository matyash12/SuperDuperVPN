from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import *

class PeerTests(TestCase):
    def setUp(self):
        # Create a test user (if needed)
        self.user = User.objects.create_user(
            username='root',
            password='password'
        )
        WireGuardInterface.objects.create(
            PrivateKey='ignore',
            PublicKey='ignore',
            PreSharedKey='ignore',
        )
        Settings.objects.create(
            ServerIpAddress='0.0.0.0' 
        )

        # Log in the user (if needed)
        self.client.login(username='root', password='password')
        
    def test_peer_creation(self):
        response = self.client.get('/add_peer')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/add_peer', data=
                                                       {
                                                           'action':'add',
                                                           'Name':'TestName123',
                                                           'DNS':'8.8.8.8',
                                                           'AllowedIPs':'0.0.0.0/0, ::/0'
                                                           }
                                                       )
        
        
        self.assertEqual(response.status_code,302)
        
        url_peer_detail = response.url
        
        response = self.client.get(url_peer_detail)
        self.assertEqual(response.status_code,200)
        self.assertContains(response,'8.8.8.8')
               
    