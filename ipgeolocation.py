#!/usr/bin/env python3
# encoding: UTF-8

import json, os, socket, ipaddress, urllib.request, webbrowser, argparse, csv
from datetime import datetime
from termcolor import colored
from sys import platform as _platform

# Windows အရောင်စနစ်အတွက်
if _platform == 'win32':
    import colorama
    colorama.init()

# --- Logger & Colors ---
def Red(v): return colored(v, 'red', attrs=['bold'])
def Green(v): return colored(v, 'green', attrs=['bold'])
def Yellow(v): return colored(v, 'yellow', attrs=['bold'])

class Logger:
    def __init__(self, nolog=False):
        self.NoLog = nolog
        if not nolog and not os.path.exists('./logs'): os.makedirs('./logs')

    def PrintIPGeo(self, obj):
        print(f"\n{Green('[+] Target Info:')} {obj['query']}")
        print(f"    Country    : {obj.get('country', '-')}")
        print(f"    City       : {obj.get('city', '-')}")
        print(f"    ISP        : {obj.get('isp', '-')}")
        print(f"    Lat/Lon    : {obj.get('lat')}, {obj.get('lon')}")
        maps_link = f"https://www.google.com/maps/place/{obj.get('lat')},{obj.get('lon')}"
        print(f"    Google Maps: {Yellow(maps_link)}")
        return maps_link

# --- Main Tool Logic ---
def get_geolocation(target, open_map=False):
    logger = Logger()
    api_url = f"http://ip-api.com/json/{target}"
    
    try:
        print(f"[*] Retrieving information for: {target if target else 'My IP'}...")
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())

        if data['status'] == 'success':
            maps_url = logger.PrintIPGeo(data)
            if open_map:
                print("[*] Opening Google Maps...")
                webbrowser.open(maps_url)
        else:
            print(f"[{Red('ERROR')}] {data['message']}")
    except Exception as e:
        print(f"[{Red('ERROR')}] {e}")

# --- Argument Parser (စတင်အသုံးပြုရန်) ---
if __name__ == "__main__":
    banner = f"{Red('IPGeolocation v2.0.4')} - {Green('Real Tool')}"
    print(banner)
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--target', help='Target IP or Domain')
    parser.add_argument('-m', '--my-ip', action='store_true', help='Get info for your IP')
    parser.add_argument('-g', action='store_true', help='Open location in Google Maps')
    
    args = parser.parse_args()
    
    if args.my_ip:
        get_geolocation("", args.g)
    elif args.target:
        try:
            # Domain ဆိုရင် IP အရင်ပြောင်းမယ်
            ip = socket.gethostbyname(args.target)
            get_geolocation(ip, args.g)
        except:
            print(f"[{Red('ERROR')}] Invalid IP or Domain")
    else:
        parser.print_help()