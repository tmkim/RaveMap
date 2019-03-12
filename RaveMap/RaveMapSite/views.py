# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.conf import settings
from operator import itemgetter
from datetime import datetime
import requests
import json

def index(request):
    #resp = requests.get(build_api_call()
    r = requests.get('https://edmtrain.com/api/events?locationIds=42&client=dcd97c59-e01a-4a9a-8220-fc108e7003ff').json()

    raves = build_response_content(r)

    context = {'raves' : raves}
    #print(resp.text)

    return render(request, 'index.html', context)

def build_api_call(location=-1, radius=25):
    base_url = 'https://edmtrain.com/api/events?'
    api_key = settings.EDMTRAIN_API_KEY
    start_date = str(date.today())
    #location_ids = build_locations(location, radius)
    location_ids='94'
    api_url = '{}locationIds={}&startDate={}&client={}'

    return api_url.format(base_url, location_ids, start_date, api_key)

# def build_locations(location, radius):
#     if location == -1:
        #location = user's location

    #return string of location IDs within radius to location

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
