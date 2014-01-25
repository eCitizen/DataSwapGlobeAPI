#!/usr/bin/python

import math
import requests
import utm

def hit_api(params):
    def flatten_record(d):
        out = {k:(v[0] if len(v)>0 else None) for k,v in d['data'].items()}
        out['id'] = d['id']
        return out 
    
    r = requests.get("http://54.237.114.25/s",params=params)
    
    return map(flatten_record, r.json()['hits']['hit'])

def bounding_box(lat,lon,r):
    c = utm.from_latlon(lat,lon)
    ne = utm.to_latlon(c[0]+r,c[1]-r,c[2],c[3])
    sw = utm.to_latlon(c[0]-r,c[1]+r,c[2],c[3])
    return {'lat':(ne[0],sw[0]),'lon':(ne[1],sw[1])}

def query_point(lat,lon,r):
    def bb_string(minmax):
        return '..'.join(map(lambda x: str(int(abs(x)*1000)),minmax))
    
    bbox = bounding_box(lat,lon,r)

    query_string = "(and latitude_1k:%s longitude_1k:%s)" % (bb_string(bbox['lat']),bb_string(bbox['lon']))
    
    q = { 'key': 'dataswap',
          'start': 0,
          'size': 1,
          'return-fields': ','.join(['latitude','longitude','headline','printpublicationdate','canonicalurl']),
          'bq': query_string,
          'rank': "-printpublicationdate"}
    
    return hit_api(q)

def distance(lat1,lon1,lat2,lon2):
    utm1 = utm.from_latlon(lat1,lon1)
    utm2 = utm.from_latlon(lat2,lon2)
    w = utm2[0]-utm1[0]
    h = utm2[1]-utm1[1]
    return math.sqrt(w*w+h*h)

def main():
    stops = requests.get("https://raw.github.com/singingwolfboy/MBTA-GeoJSON/master/stops.geojson").json()
    for stop in stops['features']:
	    print stop['properties']['name']
	    ll = stop['geometry']['coordinates']
	    
	    story = query_point(ll[1],ll[0],1000)[0]
	    
	    print story['headline'], story['printpublicationdate'],distance(ll[1],ll[0],float(story['latitude']),float(story['longitude'])), "meters"

if __name__ == "__main__":
    main()