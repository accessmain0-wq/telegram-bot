#!/usr/bin/env python3
# encoding: UTF-8

import requests
import json
import sys

class IpGeoLocation:
    """IP Geolocation အချက်အလက်များကို သိမ်းဆည်းရန် Class"""
    
    def __init__(self, query, jsonData = None):
        self.Query = query
        self.ASN = '-'
        self.City = '-'
        self.Country = '-'
        self.CountryCode = '-'
        self.ISP = '-'
        self.Latitude = 0.0
        self.Longitude = 0.0 # Spelling ပြင်ထားပါတယ်
        self.Organization = '-'
        self.IP = '0.0.0.0'
        self.Region = '-'
        self.RegionName = '-'
        self.Status = '-'
        self.Timezone = '-'
        self.Zip = '-'
        self.GoogleMapsLink = ''
        
        if jsonData != None:
            if type(jsonData) is dict:
                self.ASN = jsonData.get('as', '-')
                self.City = jsonData.get('city', '-')
                self.Country = jsonData.get('country', '-')
                self.CountryCode = jsonData.get('countryCode', '-')
                self.ISP = jsonData.get('isp', '-')
                self.Latitude = jsonData.get('lat', 0.0)
                self.Longitude = jsonData.get('lon', 0.0)
                self.Organization = jsonData.get('org', '-')
                self.IP = jsonData.get('query', '0.0.0.0')
                self.Region = jsonData.get('region', '-')
                self.RegionName = jsonData.get('regionName', '-')
                self.Status = jsonData.get('status', 'fail')
                self.Timezone = jsonData.get('timezone', '-')
                self.Zip = jsonData.get('zip', '-')
                
                if self.Latitude != 0.0:
                    self.GoogleMapsLink = f'https://www.google.com/maps/place/{self.Latitude},{self.Longitude}/@{self.Latitude},{self.Longitude},16z'
                    
    def display_info(self):
        """ရလာတဲ့ အချက်အလက်တွေကို လှလှပပ ပြသရန်"""
        print("-" * 40)
        print(f" IP Address    : {self.IP}")
        print(f" Country       : {self.Country} ({self.CountryCode})")
        print(f" City/Region   : {self.City}, {self.RegionName}")
        print(f" ISP           : {self.ISP}")
        print(f" Organization  : {self.Organization}")
        print(f" Latitude      : {self.Latitude}")
        print(f" Longitude     : {self.Longitude}")
        print(f" Timezone      : {self.Timezone}")
        print(f" Google Maps   : {self.GoogleMapsLink}")
        print("-" * 40)

def get_ip_location(target_ip=""):
    """ip-api.com ကို အသုံးပြုပြီး Data ဆွဲယူသည့် Function"""
    api_url = f"http://ip-api.com/json/{target_ip}"
    
    try:
        response = requests.get(api_url)
        if response.status_status_code == 200 or 200:
            data = response.json()
            if data['status'] == 'success':
                location_obj = IpGeoLocation(target_ip, data)
                location_obj.display_info()
            else:
                print(f"[!] Error: {data['message']}")
        else:
            print("[!] API သို့ ချိတ်ဆက်၍ မရပါ။")
    except Exception as e:
        print(f"[!] ချိတ်ဆက်မှု အမှားအယွင်း ရှိနေပါသည်: {e}")

if __name__ == "__main__":
    print("--- IP GeoLocation Tracker ---")
    ip_to_track = input("စစ်ဆေးလိုသော IP ကို ရိုက်ထည့်ပါ (မိမိ IP ကို သိလိုလျှင် Enter ခေါက်ပါ): ")
    get_ip_location(ip_to_track)