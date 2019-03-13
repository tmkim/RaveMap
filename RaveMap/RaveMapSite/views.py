# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.conf import settings
from operator import itemgetter
from datetime import datetime, date
import requests
import json
import geocoder

def index(request):
    r = requests.get(build_edmt_api_call()).json()
    raves = build_response_content(r)

    context = {
                'raves' : raves,
                'gmap_url' : settings.GOOGLE_MAPS_URL
              }
    #print(resp.text)

    return render(request, 'index.html', context)

def build_edmt_api_call(city="",state="", radius=25):
    base_url = 'https://edmtrain.com/api/events?'
    api_key = settings.EDMTRAIN_API_KEY
    start_date = str(date.today())
    location_ids = build_locations(city, state, radius)
    api_url = '{}locationIds={}&startDate={}&client={}'

    return api_url.format(base_url, location_ids, start_date, api_key)

def build_locations(city, state, radius):
    base_url = 'https://edmtrain.com/api/locations?state={}&city={}&client={}'
    cities_url="http://getnearbycities.geobytes.com/GetNearbyCities?radius={}&locationcode={}&limit={}"
    loc_ids = ""

    if city == "" and state == "":
        geo = geocoder.ip('me')
        # state = geo.state.replace(" ", "%20")
        # city = geo.city.replace(" ", "%20")
    else:
        geo = geocoder.ip(city)

    rc = requests.get(cities_url.format(radius, geo.ip, radius*4)).json()

    for item in rc:
        r = requests.get(base_url.format(item[12], item[1], settings.EDMTRAIN_API_KEY)).json()
        if r['success'] == True:
            loc_ids += str(r['data'][0]['id']) + ","
        else:
            loc_ids = loc_ids #todo: error handling

    return loc_ids[:-1]

def find_cities(radius, city=""):
    if city == "":
        loc_code = geocoder.ip('me')
    else:
        loc_code = geocoder.ip(city)




def build_response_content(response):
    content = []
    if response['success'] == True:
        for item in response['data']:
            djs = ""
            for dj in item['artistList']:
                djs += dj['name'] + ", "
            event_name = item['artistList'][0]['name'] if not item['name'] else item['name']

            content.append({
                'name': event_name,
                'dateDay': datetime.strptime(item['date'], '%Y-%m-%d').strftime('%A'),
                'date': datetime.strptime(item['date'], '%Y-%m-%d').strftime('%B %d, %Y'),
                'dj': djs[:-2],
                'venue': item['venue']['name'],
                'tickets': item['ticketLink']
            })

    return content
