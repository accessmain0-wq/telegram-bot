#!/usr/bin/env python3
# encoding: UTF-8

import json
import os
import socket
import urllib.request
import urllib.parse
import webbrowser
import random
import argparse
from datetime import datetime
from termcolor import colored
from sys import platform as _platform

# Windows အတွက် အရောင်စနစ်ပြင်ဆင်ခြင်း
if _platform == 'win32':
    import colorama
    colorama.init()

# --- ၁။ Custom Exceptions (အမှားအယွင်းများ) ---
class UserAgentFileEmptyError(Exception): pass
class InvalidTargetError(Exception): pass
class TargetsFileEmptyError(Exception): pass
class TargetsFileNotSpecifiedError(Exception): pass
class UserAgentFileNotSpecifiedError(Exception): pass
class ProxyServerNotReachableError(Exception): pass

# --- ၂။ Logger & Colors ---
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
        filename = f'{datetime.now().strftime("%Y%m%d")}.log'
        path = os.path.join('./logs', filename)
        with open(path, 'a', encoding='utf-8') as f:
            f.write(f'[{messagetype}] {datetime.now()} - {message}\n')

    def PrintError(self, message):
        if not self.NoLog: self.WriteLog('ERROR', message)
        print(f"[{Red('ERROR')}] {message}")

    def Print(self, message):
        if not self.NoLog: self.WriteLog('INFO', message)
        if self.Verbose: print(f"[{Green('*')}] {message}")

    def PrintIPGeoLocation(self, obj):
        print(f"\n{Green('[+] Target: ')}{obj.Query}")
        print(f"    IP Address    : {Green(obj.IP)}")
        print(f"    Country       : {Green(obj.Country)}")
        print(f"    City          : {Green(obj.City)}")
        print(f"    ISP           : {Green(obj.ISP)}")
        print(f"    Latitude      : {Green(str(obj.Latitude))}")
        print(f"    Longitude     : {Green(str(obj.Longitude))}")
        print(f"    Google Maps   : {Yellow(obj.GoogleMapsLink)}")
        print("-" * 40)

# --- ၃။ Data Class ---
class IpGeoLocation:
    def __init__(self, query, jsonData):
        self.Query = query
        self.IP = jsonData.get('query', '-')
        self.Country = jsonData.get('country', '-')
        self.City = jsonData.get('city', '-')
        self.ISP = jsonData.get('isp', '-')
        self.Latitude = jsonData.get('lat', 0.0)
        self.Longitude = jsonData.get('lon', 0.0)
        self.GoogleMapsLink = f"https://www.google.com/maps/place/{self.Latitude},{self.Longitude}"

# --- ၄။ Main Library Logic ---
class IpGeoLocationLib:
    def __init__(self, logger):
        self.Logger = logger
        self.BaseURL = "http://ip-api.com/json/{}"

    def GetInfo(self, target, open_maps=False, uagent=None):
        try:
            # Domain ကို IP ပြောင်းခြင်း
            try:
                socket.inet_aton(target)
                query_ip = target
            except:
                if target == "":
                    query_ip = ""
                else:
                    self.Logger.Print(f"Resolving {target}...")
                    query_ip = socket.gethostbyname(target)

            self.Logger.Print(f"Retrieving data for {target if target else 'Your IP'}...")
            
            headers = {'User-Agent': uagent or 'IPGeoLocation/2.0'}
            req = urllib.request.Request(self.BaseURL.format(query_ip), headers=headers)
            
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())

            if data['status'] == 'success':
                obj = IpGeoLocation(target if target else "MyIP", data)
                self.Logger.PrintIPGeoLocation(obj)
                if open_maps:
                    webbrowser.open(obj.GoogleMapsLink)
            else:
                raise InvalidTargetError(data['message'])

        except Exception as e:
            self.Logger.PrintError(f"Error: {str(e)}")

# --- ၅။ Command Line Interface ---
def main():
    banner = f"""
    {Red('IPGeolocation Tool')} - {Yellow('Version 2.0')}
    {Green('Powered by ip-api.com')}
    """
    print(banner)

    parser = argparse.ArgumentParser(description="Get Geolocation info from IP/Domain")
    parser.add_argument('-t', '--target', help='Target IP or Domain')
    parser.add_argument('-m', '--my-ip', action='store_true', help='Get info for your own IP')
    parser.add_argument('-g', action='store_true', help='Open in Google Maps')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--nolog', action='store_true', help='Disable logging')

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