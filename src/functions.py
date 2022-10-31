from pymongo import MongoClient
import pandas as pd
import os
import requests
import json
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import re
import geopandas as gpd
from cartoframes.viz import Map, Layer, popup_element
import numpy as np

import folium
from folium import Choropleth, Circle, Marker, Icon, Map
from folium.plugins import HeatMap, MarkerCluster


def extract_company(filter_, c):
    projection = {"_id":0, "name":1, "category_code":1, "tag_list":1, "total_money_raised":1, "offices.city":1, "offices.state_code": 1, "offices.country_code":1,"offices.latitude": 1, "offices.longitude": 1}
    list_ = list(c.find(filter_, projection))
    
    df = pd.DataFrame(list_).explode("offices").reset_index(drop=True)
    df = pd.concat([df, df["offices"].apply(pd.Series)], axis=1).reset_index(drop=True)
    df = df.drop(["offices"], axis = 1)
    df = df[df["city"]!=""]
    
    return df


def foursquare_cat (category, name, df): # v2
    response_list = []
    distance = []
    lat = []
    lon = []
    
    for i in range(len(df)):
        url = f"https://api.foursquare.com/v3/places/search?ll={df['latitude'][i]}%2C{df['longitude'][i]}&categories={category}&limit=1"
        headers = {"accept": "application/json", "Authorization": token_fsq}
        response = requests.get(url, headers=headers).json()
        
        response_list.append(response)
        
    for x in range(len(response_list)):
        try:
            distance.append(response_list[x]["results"][0]["distance"])
        except:
            distance.append(None)
            

    for x in range(len(response_list)):
        try:
            lat.append(response_list[x]["results"][0]["geocodes"]["main"]["latitude"])
        except:
            lat.append(None)
            

    for x in range(len(response_list)):
        try:
            lon.append(response_list[x]["results"][0]["geocodes"]["main"]["longitude"])


        except:
            lon.append(None)


            

        
    df[f"{name}_dist"] = distance
    df[f"{name}_lat"] = lat
    df[f"{name}_lon"] = lon


    
    return df


def foursquare_query (query, df): # v2
    response_list = []
    distance = []
    lat = []
    lon = []
    
    for i in range(len(df)):
        url = f"https://api.foursquare.com/v3/places/search?query={query}&ll={df['latitude'][i]}%2C{df['longitude'][i]}&sort=DISTANCE&limit=1"
        headers = {"accept": "application/json", "Authorization": token_fsq}
        response = requests.get(url, headers=headers).json()
        
        response_list.append(response)

        
        
    for x in range(len(response_list)):
        try:
            distance.append(response_list[x]["results"][0]["distance"])
        except:
            distance.append(None)
            

    for x in range(len(response_list)):
        try:
            lat.append(response_list[x]["results"][0]["geocodes"]["main"]["latitude"])
        except:
            lat.append(None)
            

    for x in range(len(response_list)):
        try:
            lon.append(response_list[x]["results"][0]["geocodes"]["main"]["longitude"])


        except:
            lon.append(None)
        
    df[f"{query}_dist"] = distance
    df[f"{query}_lat"] = lat
    df[f"{query}_lon"] = lon
    
    
    return df

def distance(df):
    score = []
    for i in range(len(df)):
        airport = df["airport_dist"][i]
        starbucks = df["starbucks_dist"][i]
        night_club = df["n_club_dist"][i]
        basket = df["b_stadium_dist"][i]
        school = df["school_dist"][i]
        total_score = (1/airport * 0.30)*100 + (1/starbucks * 0.25)*100 + (1/night_club * 0.20)*100 + (1/basket * 0.15)*100 + (1/school * 0.10)*100
        score.append(total_score)
        
    df["score"] = score
    
    return df
            
            
