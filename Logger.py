#!/usr/bin/env python3
# encoding: UTF-8

import json
import os
import socket
import urllib.request
from datetime import datetime
from termcolor import colored
from sys import platform as _platform

# Windows အတွက် အရောင်စနစ်ပြင်ဆင်ခြင်း
if _platform == 'win32':
    import colorama
    colorama.init()

# --- အရောင်သတ်မှတ်ချက်များ ---
def Red(value):
    return colored(value, 'red', attrs=['bold'])

def Green(value):
    return colored(value, 'green', attrs=['bold'])

def Yellow(value):
    return colored(value, 'yellow', attrs=['bold'])

# --- ၁။ Data Class (အချက်အလက်သိမ်းဆည်းရန်) ---
class IpGeoLocation:
    def __init__(self, query, jsonData=None):
        self.Query = query
        self.ASN = jsonData.get('as', '-')
        self.City = jsonData.get('city', '-')
        self.Country = jsonData.get('country', '-')
        self.CountryCode = jsonData.get('countryCode', '-')
        self.ISP = jsonData.get('isp', '-')
        self.Latitude = jsonData.get('lat', 0.0)
        self.Longtitude = jsonData.get('lon', 0.0)
        self.Organization = jsonData.get('org', '-')
        self.IP = jsonData.get('query', '0.0.0.0')
        self.Region = jsonData.get('region', '-')
        self.RegionName = jsonData.get('regionName', '-')
        self.Timezone = jsonData.get('timezone', '-')
        self.Zip = jsonData.get('zip', '-')
        self.GoogleMapsLink = f'https://www.google.com/maps/place/{self.Latitude},{self.Longtitude}/@{self.Latitude},{self.Longtitude},16z'

# --- ၂။ Logger Class (စာသားထုတ်ပြန်ရန်နှင့် Log သိမ်းရန်) ---
class Logger:
    def __init__(self, nolog=False, verbose=False):
        self.NoLog = nolog
        self.Verbose = verbose
        if not os.path.exists('./logs'):
            os.makedirs('./logs')

    def WriteLog(self, messagetype, message):
        filename = '{}.log'.format(datetime.strftime(datetime.now(), "%Y%m%d"))
        path = os.path.join('.', 'logs', filename)
        with open(path, 'a', encoding='utf-8') as logFile:
            logFile.write('[{}] {} - {}\n'.format(messagetype, datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"), message))

    def PrintError(self, message):
        if not self.NoLog:
            self.WriteLog('ERROR', message)
        print('[{}] {}'.format(Red('ERROR'), message))

    def PrintResult(self, title, value):
        print('{}: {}'.format(title, Green(value)))

    def Print(self, message):
        if not self.NoLog:
            self.WriteLog('INFO', message)
        print('[{}] {}'.format(Green('*'), message))

    def PrintIPGeoLocation(self, ipGeo):
        self.PrintResult('\n[+] Target', ipGeo.Query)
        self.PrintResult('    IP', ipGeo.IP)
        self.PrintResult('    ASN', ipGeo.ASN)
        self.PrintResult('    City', ipGeo.City)
        self.PrintResult('    Country', ipGeo.Country)
        self.PrintResult('    ISP', ipGeo.ISP)
        self.PrintResult('    Latitude', str(ipGeo.Latitude))
        self.PrintResult('    Longitude', str(ipGeo.Longtitude))
        self.PrintResult('    Timezone', ipGeo.Timezone)
        self.PrintResult('    Google Maps', ipGeo.GoogleMapsLink)
        print()

# --- ၃။ Main Logic (အဓိကအလုပ်လုပ်ပုံ) ---
def track_ip(target):
    logger = Logger(verbose=True)
    api_url = "http://ip-api.com/json/{}"
    
    try:
        # IP ဟုတ်မဟုတ် စစ်ဆေးခြင်း
        try:
            socket.inet_aton(target)
            query_ip = target
        except:
            if target == "":
                query_ip = ""
            else:
                logger.Print(f"Resolving hostname: {target}...")
                query_ip = socket.gethostbyname(target)

        logger.Print(f"Retrieving Geolocation for {target if target else 'Local IP'}...")
        
        req = urllib.request.Request(api_url.format(query_ip))
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())

        if data['status'] == 'success':
            ip_obj = IpGeoLocation(target if target else data['query'], data)
            logger.PrintIPGeoLocation(ip_obj)
        else:
            logger.PrintError(f"Failed: {data['message']}")

    except Exception as e:
        logger.PrintError(f"An error occurred: {e}")

if __name__ == "__main__":
    print(Yellow("""
    =========================================
    |       IP GEOLOCATION TRACKER          |
    |       Powered by ip-api.com           |
    =========================================
    """))
    ip_address = input("Enter Target IP or Domain (Press Enter for My IP): ").strip()
    track_ip(ip_address)