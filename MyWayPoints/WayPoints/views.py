from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse

import googlemaps
import requests as re
import json

import reverse_geocoder

from .models import PlaceWeather  # Importing model

# Create your views here.

def clientDirection(request):
    return render(request, 'WayPoints/clientDirection.html')


def test(request):
    return HttpResponse("Testing URL")  # testing purpose

def singleMarker(request):
    return render(request, 'WayPoints/singleMarker.html')  # Just to show a single marker on the map

def stylishMap(request):
    return render(request, 'WayPoints/stylishMap.html')


def input(request):

    if request.method == "POST":   # taking user input

        origin = request.POST['origin']
        destination = request.POST['destination']

        # https://djangobook.com/django-models-basic-data-access/


        records = PlaceWeather.objects.filter(origiN=origin,destinatioN=destination)

        if len(records) > 0:

            points_with_weather = []

            for record in records:

                point_with_weather = {
                    'origin': origin,
                    'destination': destination,
                    'latitude': float(record.latitudE),
                    'longitude': float(record.longitudE),
                    'city': record.citY,
                    'temperature': record.temperaturE,
                    'humidity': record.humiditY,
                    'pressure': record.pressurE,
                    'description': record.descriptioN,
                    'icon': record.icoN
                }
                points_with_weather.append(point_with_weather)

            context = {'data': json.dumps(points_with_weather)}
            return render(request, 'WayPoints/serverDirection.html', context)

        else:
            # Need API Call
            # References : https://googlemaps.github.io/google-maps-services-python/docs/
            # https://github.com/googlemaps/google-maps-services-python

            '''
              GOOGLE API CALLING
            '''
            # Creating client with API KEY
            gmaps = googlemaps.Client(key='add your key')

            # Calling google DIRECTION API with the given value , returns - list of routes
            directions_result = gmaps.directions(origin, destination, mode="driving")

            steps = directions_result[0]['legs'][0]['steps']

            points_with_weather = []  # Each element of this list will be a dictionary

            for i, step in enumerate(steps):
                # Taking only half steps
                if i % 3 == 0 or i % 3 == 1:
                    continue
                latitude = step['end_location']['lat']
                longitude = step['end_location']['lng']

                # https://pypi.org/project/reverse_geocoder/
                coordinates = (latitude,longitude)
                res = reverse_geocoder.search(coordinates)
                city = res[0]['name']

                '''
                          WEATHER API CALLING
                '''

                url = 'http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&units=imperial&appid={}'
                key = 'add your key'
                weather_response = re.get(url.format(latitude, longitude, key)).json()
                # print(weather_response)

                point_with_weather = {
                    'origin' : origin,
                    'destination' : destination,
                    'latitude': latitude,
                    'longitude': longitude,
                    'city' : city,
                    'temperature': weather_response['main']['temp'],
                    'humidity': weather_response['main']['humidity'],
                    'pressure': weather_response['main']['pressure'],
                    'description': weather_response['weather'][0]['description'],
                    'icon': weather_response['weather'][0]['icon']
                }

                points_with_weather.append(point_with_weather)  # Insert the dictionary into the list

            # Save the data into Database
            for point in points_with_weather:
                temp = PlaceWeather(origiN=origin,
                                    destinatioN=destination,
                                    citY = point['city'],
                                    latitudE=point['latitude'],
                                    longitudE=point['longitude'],
                                    temperaturE=point['temperature'],
                                    humiditY=point['humidity'],
                                    pressurE=point['pressure'],
                                    descriptioN=point['description'],
                                    icoN=point['icon']
                                    )
                temp.save()

            context = {'data': json.dumps(points_with_weather)}
            # return HttpResponse(points_with_weather)

            return render(request, 'WayPoints/serverDirection.html', context)

    else:
        return render(request, 'WayPoints/input.html')




