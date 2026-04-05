#!/usr/bin/env python3
# encoding: UTF-8

import json
import urllib.request
import urllib.parse
import socket
import sys
import webbrowser

# --- အခြေခံလိုအပ်သော Class များ ---

class IpGeoLocation:
    """IP မှရသော အချက်အလက်များကို သိမ်းဆည်းရန်"""
    def __init__(self, query, jsonData=None):
        self.IP = jsonData.get('query', '0.0.0.0')
        self.City = jsonData.get('city', '-')
        self.Country = jsonData.get('country', '-')
        self.ISP = jsonData.get('isp', '-')
        self.Latitude = jsonData.get('lat', 0.0)
        self.Longitude = jsonData.get('lon', 0.0)
        self.Timezone = jsonData.get('timezone', '-')
        self.GoogleMapsLink = f'https://www.google.com/maps/place/{self.Latitude},{self.Longitude}'

class Logger:
    """စာသားများကို Print ထုတ်ရန်"""
    def Print(self, message):
        print(f"[*] {message}")
    def PrintError(self, message):
        print(f"[!] ERROR: {message}")
    def PrintIPGeoLocation(self, obj):
        print("\n" + "="*30)
        print(f" IP Address    : {obj.IP}")
        print(f" Country       : {obj.Country}")
        print(f" City          : {obj.City}")
        print(f" ISP           : {obj.ISP}")
        print(f" Latitude      : {obj.Latitude}")
        print(f" Longitude     : {obj.Longitude}")
        print(f" Timezone      : {obj.Timezone}")
        print(f" Google Maps   : {obj.GoogleMapsLink}")
        print("="*30 + "\n")

class Utils:
    """အကူအညီပေးမည့် လုပ်ဆောင်ချက်များ"""
    def isValidIPAddress(self, ip):
        try:
            socket.inet_aton(ip)
            return True
        except:
            return False

    def hostnameToIP(self, hostname):
        try:
            return socket.gethostbyname(hostname)
        except:
            return None

    def openLocationInGoogleMaps(self, obj):
        print(f"[*] Opening Google Maps: {obj.GoogleMapsLink}")
        webbrowser.open(obj.GoogleMapsLink)

# --- အဓိက လုပ်ဆောင်ချက် Class ---

class IpGeoLocationLib:
    def __init__(self, target, logger):    
        self.RequestURL = 'http://ip-api.com/json/{}'
        self.Target = target
        self.Logger = logger
        self.Utils = Utils()
        self.UserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'

    def GetInfo(self, open_maps=False):
        try:
            target = self.Target
            if not target:
                query_target = "" # မိမိ IP ကို ကြည့်မည်
            elif self.Utils.isValidIPAddress(target):
                query_target = target
            else:
                ip = self.Utils.hostnameToIP(target)
                if not ip:
                    self.Logger.PrintError("Invalid Domain or IP!")
                    return
                query_target = ip

            self.Logger.Print(f"Retrieving data for {target if target else 'Your IP'}...")
            
            # API သို့ ချိတ်ဆက်ခြင်း
            req = urllib.request.Request(self.RequestURL.format(query_target), headers={'User-Agent': self.UserAgent})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())

            if data.get('status') == 'success':
                result = IpGeoLocation(target, data)
                self.Logger.PrintIPGeoLocation(result)
                
                if open_maps:
                    self.Utils.openLocationInGoogleMaps(result)
            else:
                self.Logger.PrintError(f"API Error: {data.get('message')}")

        except Exception as e:
            self.Logger.PrintError(f"An unexpected error occurred: {e}")

# --- စတင်အသုံးပြုခြင်း ---

if __name__ == "__main__":
    print("""
    ###############################
    #    IP Geolocation Tool      #
    #    Real GPS Link Generator  #
    ###############################
    """)
    
    target_input = input("Enter IP or Domain (Press Enter for My IP): ").strip()
    map_choice = input("Open Google Maps in browser? (y/n): ").lower()
    
    logger = Logger()
    lib = IpGeoLocationLib(target_input, logger)
    
    should_open_map = True if map_choice == 'y' else False
    lib.GetInfo(open_maps=should_open_map)