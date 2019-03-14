# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from django.db import models

# Create your models here.
class Rave_Event(models.Model):
    title = models.CharField(max_length=200)
    artists = models.TextField()
    location = models.TextField()
    date = models.DateTimeField()
    ticket_link = models.TextField()

class Venue(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    location = models.TextField()
    address = models.TextField()
    state = models.TextField()
    longitude = models.FloatField()
    latitude = models.FloatField()

class Location(models.Model):
    state = models.TextField()
    city = models.TextField()
    longitude = models.FloatField()
    latitude = models.FloatField()
