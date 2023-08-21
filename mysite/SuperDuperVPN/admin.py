from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(WireGuardConfigFile)
admin.site.register(WireGuardInterface)
admin.site.register(WireGuardPeer)