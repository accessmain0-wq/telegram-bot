#!/usr/bin/env python3
# encoding: UTF-8

import json
import os
import socket
import ipaddress
import urllib.request
import urllib.parse
import webbrowser
import argparse
from datetime import datetime
from subprocess import call
from termcolor import colored
from sys import platform as _platform

# Windows အတွက် အရောင်စနစ်ပြင်ဆင်ခြင်း
if _platform == 'win32':
    import colorama
    colorama.init()

# --- ၁။ Custom Exceptions (အမှားအယွင်းများ) ---
class ProxyServerNotReachableError(Exception): pass
class InvalidTargetError(Exception): pass

# --- ၂။ Logger & Colors (အရောင်နှင့် မှတ်တမ်း) ---
def Red(value): return colored(value, 'red', attrs=['bold'])
def Green(value): return colored(value, 'green', attrs=['bold'])
def Yellow(value): return colored(value, 'yellow', attrs=['bold'])

class Logger:
    def __init__(self, nolog=False, verbose=False):
        self.NoLog = nolog
        self.Verbose = verbose
        if not nolog and not os.path.exists('./logs'):
            os.makedirs('./logs')

    def WriteLog(self, messagetype, message):
        if self.NoLog: return
        filename = f'{datetime.now().strftime("%Y%m%d")}.log'
        path = os.path.join('./logs', filename)
        with open(path, 'a', encoding='utf-8') as f:
            f.write(f'[{messagetype}] {datetime.now()} - {message}\n')

    def PrintError(self, message):
        self.WriteLog('ERROR', message)
        print(f"[{Red('ERROR')}] {message}")

    def Print(self, message):
        self.WriteLog('INFO', message)
        if self.Verbose: print(f"[{Green('*')}] {message}")

    def PrintResult(self, title, value):
        print(f"{title}: {Green(value)}")

    def PrintIPGeoLocation(self, obj):
        print(f"\n{Green('[+] Target: ')}{obj.Query}")
        self.PrintResult("    IP Address", obj.IP)
        self.PrintResult("    Country   ", obj.Country)
        self.PrintResult("    City      ", obj.City)
        self.PrintResult("    ISP       ", obj.ISP)
        self.PrintResult("    Location  ", f"{obj.Latitude}, {obj.Longitude}")
        self.PrintResult("    Timezone  ", obj.Timezone)
        self.PrintResult("    Google Maps", obj.GoogleMapsLink)
        print("-" * 50)

# --- ၃။ Data Class (အချက်အလက် သိမ်းဆည်းရန်) ---
class IpGeoLocation:
    def __init__(self, query, jsonData):
        self.Query = query
        self.IP = jsonData.get('query', '-')
        self.Country = jsonData.get('country', '-')
        self.City = jsonData.get('city', '-')
        self.ISP = jsonData.get('isp', '-')
        self.Latitude = jsonData.get('lat', 0.0)
        self.Longitude = jsonData.get('lon', 0.0)
        self.Timezone = jsonData.get('timezone', '-')
        self.GoogleMapsLink = f"https://www.google.com/maps/place/{self.Latitude},{self.Longitude}/@{self.Latitude},{self.Longitude},16z"

# --- ၄။ Utils Class (အကူအညီပေးမည့် လုပ်ဆောင်ချက်များ) ---
class Utils:
    def __init__(self, logger):
        self.Logger = logger

    def openLocationInGoogleMaps(self, ipGeoObj):
        self.Logger.Print('Opening Geolocation in browser...')
        if _platform == 'cygwin':
            call(['cygstart', ipGeoObj.GoogleMapsLink])
        elif _platform in ['win32', 'linux', 'linux2', 'darwin']:
            webbrowser.open(ipGeoObj.GoogleMapsLink)
        else:
            self.Logger.PrintError('Cannot open browser on this platform.')

    def hostnameToIP(self, hostname):
        try:
            return socket.gethostbyname(hostname)
        except:
            return False

    def isValidIPAddress(self, ip):
        try:
            ipaddress.ip_address(ip)
            return True
        except:
            return False

# --- ၅။ Main Library Logic ---
class IpGeoLocationLib:
    def __init__(self, logger):
        self.Logger = logger
        self.Utils = Utils(logger)
        self.BaseURL = "http://ip-api.com/json/{}"

    def GetInfo(self, target, open_maps=False, uagent=None):
        try:
            query_ip = target
            if not target:
                query_ip = "" # Local IP
            elif not self.Utils.isValidIPAddress(target):
                self.Logger.Print(f"Resolving {target}...")
                query_ip = self.Utils.hostnameToIP(target)
                if not query_ip:
                    raise InvalidTargetError(f"Could not resolve {target}")

            headers = {'User-Agent': uagent or 'IPGeolocation/2.0'}
            req = urllib.request.Request(self.BaseURL.format(query_ip), headers=headers)
            
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())

            if data['status'] == 'success':
                obj = IpGeoLocation(target if target else "MyIP", data)
                self.Logger.PrintIPGeoLocation(obj)
                if open_maps:
                    self.Utils.openLocationInGoogleMaps(obj)
            else:
                self.Logger.PrintError(f"API Error: {data['message']}")

        except Exception as e:
            self.Logger.PrintError(f"{str(e)}")

# --- ၆။ Main Program Interface ---
def main():
    banner = f"""
    {Red('IPGeolocation Tool v2.0')}
    {Yellow('Powered by ip-api.com')}
    """
    print(banner)

    parser = argparse.ArgumentParser(description="Retrieve Geolocation information from IP or Domain")
    parser.add_argument('-t', '--target', help='Target IP Address or Domain')
    parser.add_argument('-m', '--my-ip', action='store_true', help='Get Geolocation for your own IP')
    parser.add_argument('-g', action='store_true', help='Open location in Google Maps')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--nolog', action='store_true', help='Disable log file saving')

    args = parser.parse_args()
    logger = Logger(nolog=args.nolog, verbose=args.verbose)
    tool = IpGeoLocationLib(logger)

    if args.my_ip:
        tool.GetInfo("", open_maps=args.g)
    elif args.target:
        tool.GetInfo(args.target, open_maps=args.g)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()