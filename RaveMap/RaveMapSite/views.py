# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from operator import itemgetter
from datetime import datetime, date
from .models import Venue, Location
from math import radians, cos, sin, asin, sqrt
from geopy.geocoders import Nominatim
import requests
import json
import geocoder

def index(request):
    g = geocoder.ip('me')
    clat = g.latlng[0]
    clng = g.latlng[1]

    venues = get_nearby_venues(clat, clng, 15)
    locations = get_locations()

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

    context = {
                'venues': venues,
                'locations': locations,
                'clat' : clat,
                'clng' : clng,
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

def search_map(request):
    bound_s = float(request.GET.get('bounds', None))
    bound_w = float(request.GET.get('boundw', None))
    bound_n = float(request.GET.get('boundn', None))
    bound_e = float(request.GET.get('bounde', None))

    venues = Venue.objects.all()
    venue_search = []

    for v in venues:
        if bound_w < bound_e:
            if bound_s <= v.latitude and v.latitude <= bound_n:
                if bound_w <= v.longitude and v.longitude <= bound_e:
                    venue_search.append({
                        'id': v.id,
                        'name': v.name,
                        'address': v.address,
                        'lat': v.latitude,
                        'lng': v.longitude
                    })
        else: #bound_e < bound_w
            if bound_s <= v.latitude and v.latitude <= bound_n:
                if bound_w <= v.longitude or v.longitude <= bound_e:
                    venue_search.append({
                        'id': v.id,
                        'name': v.name,
                        'address': v.address,
                        'lat': v.latitude,
                        'lng': v.longitude
                    })

    data = {
        'venues': venue_search
    }
    return JsonResponse(data);

def change_city(request):
    new_city = request.GET.get('city', None)
    g = Nominatim(user_agent="RaveMapSite")
    loc = g.geocode(new_city)

    clat = loc.latitude
    clng = loc.longitude
    venues = get_nearby_venues(clat, clng, 15)
    venue_list = []
    for v in venues:
        venue_list.append({
            'id': v.id,
            'name': v.name,
            'address': v.address,
            'lat': v.latitude,
            'lng': v.longitude
        })

    data = {
        'clat': clat,
        'clng': clng,
        'venues': venue_list
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

def get_locations():
    venues = Venue.objects.all()
    location_flags=[]
    locations = []
    for v in venues:
        if not (v.location in location_flags):
            loc = v.location.split(',')
            locations.append({
                'city': loc[0],
                'state': loc[1],
                'location': v.location
            })
            location_flags.append(v.location)

    return sorted(locations, key=lambda x: x['state'])

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
