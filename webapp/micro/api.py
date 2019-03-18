import requests
import os
import pickle
from flask import current_app

from micro import db, cache, cache_timeout
from micro.models import GeoIP


# Collect HTTP_X_FORWARDED_FOR if exist as it will contain real client IP
# instead of proxy or router. If not exist, collect REMOTE_ADDR as
# a backup plan.
def GetUserIP(req):
    if req.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return req.environ['REMOTE_ADDR']
    else:
        return req.environ['HTTP_X_FORWARDED_FOR']


# API call to collect geolocation information
# based on client IP address
def Geolocation_ApiCall(ip):
    url = 'https://api.ipdata.co/'+ip
    headers = {'Accept': 'application/json'}
    key = os.getenv('GEOLOC_KEY')
    payload = {'api-key': key}
    r = requests.get(url, headers=headers, params=payload)

    if r.status_code == 200:
        try:
            return r.json()
        except ValueError:
            return {'ip': ip, 'error': 'No Geolocation data could be decoded'}


# 
def Geolocation(ip):
    geoip = GeoIP.query.filter_by(ip=ip).first()
    if geoip is not None:
        update_threat(ip)
        return geoip
    else:
        geo = Geolocation_ApiCall(ip)
        if geo is not None:
            threat = calculate_threat(geo['threat'])
            g = GeoIP(ip=ip, 
                      city=geo['city'],
                      region=geo['region'],
                      country_name=geo['country_name'],
                      country_code=geo['country_code'],
                      continent=geo['continent_name'],
                      latitude=geo['latitude'],
                      longitude=geo['longitude'],
                      postal=geo['postal'],
                      flag=geo['flag'],
                      currency_name=geo['currency']['name'],
                      currency_code=geo['currency']['code'],
                      threat=threat)
            db.session.add(g)
            db.session.commit()
        

def calculate_threat(threat):
    r = False
    for _, v in threat.items():
        if v:
            r = True
            break
    
    return r


def update_threat(ip):
    geo = Geolocation_ApiCall(ip)
    g = GeoIP.query.filter_by(ip=ip).first()
    g.threat = calculate_threat(geo['threat'])
    db.session.commit()


def Currency_Change_Rate(user_currency):
    r_key = f'currency:{user_currency}'
    cached = cache.get(r_key)
    if cached:
        current_app.logger.info('currency is cached')
        return pickle.loads(cached)

    url = 'https://free.currencyconverterapi.com/api/v6/convert'
    headers = {'Accept': 'application/json'}
    payload = {}
    key = os.getenv('CURRENCY_KEY')

    s = f'{user_currency}_USD,{user_currency}_EUR,{user_currency}_JPY,{user_currency}_CAD'
    payload = {'q': s, 'compact': 'ultra', 'apiKey': key}
    r = requests.get(url, headers=headers, params=payload)
    if r.status_code == 200:
        try:
            j = r.json()
            d = {'USD': j[f'{user_currency}_USD'],
                 'EUR': j[f'{user_currency}_EUR'],
                 'JPY': j[f'{user_currency}_JPY'],
                 'CAD': j[f'{user_currency}_CAD']}
            cache.setex(name=r_key,
                        time=cache_timeout,
                        value=pickle.dumps(d))
            return d
        except ValueError:
            return {'error': 'No Currency data could be decoded'}
        


def GetWeather(data):
    r_key = f'weather:{data.ip}'
    cached = cache.get(r_key)
    if cached:
        return pickle.loads(cached)

    weather_key = os.getenv('WEATHER_KEY')
    url = 'http://api.openweathermap.org/data/2.5/weather'
    headers = {'Accept': 'application/json'}

    payload = {'q': f'{data.city},{data.country_code}', 
               'appid': 'f300045f7fc5531aceac891d85661b98'}
    r = requests.get(url, headers=headers, params=payload)
    if r.status_code == 200:
        try:
            t = r.json()
            weather = {'cityid': t['id'], 'key': weather_key}
            cache.setex(name=r_key,
                        time=cache_timeout,
                        value=pickle.dumps(weather))
            return weather
        except ValueError:
            return {'error': 'No Currency data could be decoded'}
    elif r.status_code == 404:
        payload = {'zip': f'{data.postal},{data.country_code}', 
                   'appid': weather_key}
        r = requests.get(url, headers=headers, params=payload)
        if r.status_code == 200:
            try:
                t = r.json()
                weather = {'cityid': t['id'], 'key': weather_key}
                cache.setex(name=r_key,
                            time=cache_timeout,
                            value=pickle.dumps(weather))
                return weather
            except ValueError:
                return {'error': 'No Currency data could be decoded'}
        elif r.status_code == 404:
            payload = {'lat': int(data.latitude), 'lon': int(data.longitude), 
                       'appid': weather_key}
            r = requests.get(url, headers=headers, params=payload)
            if r.status_code == 200:
                try:
                    t = r.json()
                    weather = {'cityid': t['id'], 'key': weather_key}
                    cache.setex(name=r_key,
                                time=cache_timeout,
                                value=pickle.dumps(weather))
                    return weather
                except ValueError:
                    return {'error': 'No Currency data could be decoded'}
