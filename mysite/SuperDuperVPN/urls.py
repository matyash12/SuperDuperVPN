from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("view", views.view, name="view"),
    path("edit_interface", views.edit_interface, name="edit_interface"),
    path("peers", views.peers, name="peers"),
    path("edit_peer/<int:peer_id>/", views.edit_peer, name="edit_peer"),
    path("add_peer/<int:pk>/", views.add_peer, name="add_peer"),
    path('download_wireguard_client_config/<str:name_of_the_file>', views.download_wireguard_client_config,name='download_wireguard_client_config'),
    path('qr_code_viewer/<str:name_of_the_file>',views.qr_code_viewer,name='qr_code_viewer'),
    path("settings", views.server_settings, name="settings"),
    path("add_peer_name", views.add_peer_name, name="add_peer_name"),
]