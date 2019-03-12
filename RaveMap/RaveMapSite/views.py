# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.conf import settings
from datetime import date
import requests
from .models import RaveEvent

def index(request):
    base_url = 'https://edmtrain.com/api/events?'
    api_key = settings.EDMTRAIN_API_KEY
    start_date = str(date.today())
    location_ids = {} #default to user location + 25mi radius
    api_url = '{}locationIds={}&startDate={}&client={}'
    location = '94'

    #resp = requests.get(api_url.format(base_url, location_ids, start_date, api_key)).json()
    #print(resp.text)

    return render(request, 'index.html')
