# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from operator import itemgetter
from datetime import datetime, date
from .models import Venue, Location
from math import radians, cos, sin, asin, sqrt
import requests
import json
import geocoder

def index(request):
    g = geocoder.ip('me')
    r = requests.get(build_edmt_api_call(g.latlng[0], g.latlng[1])).json()
    raves = build_response_content(r)

    venues = get_nearby_venues(g.latlng[0], g.latlng[1], 15)
    markers = []

    # with requests.Session() as session:
    #     for v in venues:
    #         v.address = v.address[:-11]
    #         m = geocoder.google("51 Stuart St, Boston MA", session=session)
    #         markers.append(m)

    # venues = Venue.objects.all()
    # if not venues.exists():
    #     insert_venues_into_db()

    # locs = Location.objects.all()
    # if not locs.exists():
    #     insert_locs_into_db()

    #remove the above code
    #get list of nearby venues
    #populate venues on map

    context = {
                # 'markers': markers,
                'venues': venues,
                'raves' : raves,
                'clat' : g.latlng[0],
                'clng' : g.latlng[1],
                'gmap_url' : settings.GOOGLE_MAPS_URL
              }
    #print(resp.text)

    return render(request, 'index.html', context)

def show_raves(request):
    r = requests.get(get_raves_by_venue(request.GET.get('venue_id', None))).json()
    raves = build_response_content(r)
    data = {
        'raves': raves
    }
    return JsonResponse(data)

def get_raves_by_venue(venue_Id):
    base_url = 'https://edmtrain.com/api/events?'
    api_key = settings.EDMTRAIN_API_KEY
    api_url = '{}venueIds={}&client={}'

    return api_url.format(base_url, venue_Id, api_key)

def build_edmt_api_call(lat,long, radius=15):
    base_url = 'https://edmtrain.com/api/events?'
    api_key = settings.EDMTRAIN_API_KEY
    start_date = str(date.today())
    venues = get_nearby_venues(lat, long, radius)
    venue_ids = ""
    for v in venues:
        venue_ids += str(v.id) + ","
    api_url = '{}venueIds={}&startDate={}&client={}'

    return api_url.format(base_url, venue_ids[:-1], start_date, api_key)

def get_distance(start_lat, start_long, venue_lat, venue_long):
    slat = radians(start_lat)
    vlat = radians(venue_lat)
    dlat = vlat - slat
    dlng = radians(venue_long - start_long)
    a = sin(dlat/2.0)**2+cos(slat)*cos(vlat)*sin(dlng/2.0)**2
    c = 2 * asin(sqrt(a))

    return c * 3956 #miles

def get_nearby_venues(lat, long, radius):
    venues = Venue.objects.all()
    near_venues = []
    for v in venues:
        d = get_distance(lat, long, v.latitude, v.longitude)
        if d < radius:
            near_venues.append(v)

    return near_venues

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

    # def insert_venues_into_db():
    #     url = 'https://edmtrain.com/api/events?client={}'
    #     r = requests.get(url.format(settings.EDMTRAIN_API_KEY)).json()
    #     if r['success'] == True:
    #         for e in r['data']:
    #             try:
    #                 Venue.objects.get(id=e['venue']['id'])
    #             except Venue.DoesNotExist:
    #                 i = Venue(
    #                     id=e['venue']['id'],
    #                     name = e['venue']['name'],
    #                     location = e['venue']['location'],
    #                     address = e['venue']['address'],
    #                     state = e['venue']['state'],
    #                     longitude = e['venue']['longitude'],
    #                     latitude = e['venue']['latitude']
    #                 )
    #                 i.save()

    # def insert_locs_into_db():
