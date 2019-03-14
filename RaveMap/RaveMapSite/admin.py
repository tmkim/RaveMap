# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import Rave_Event, Venue, Location
from django.contrib import admin

# Register your models here.
admin.site.register(Rave_Event)
admin.site.register(Venue)
admin.site.register(Location)
