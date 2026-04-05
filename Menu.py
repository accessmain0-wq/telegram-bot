#!/usr/bin/env python3
# encoding: UTF-8

import argparse
import os
import json
import socket
import urllib.request
import urllib.parse
import webbrowser
from datetime import datetime
from termcolor import colored
from sys import platform as _platform

# Windows အရောင်စနစ်အတွက်
if _platform == 'win32':
    import colorama
    colorama.init()

# --- အခြေခံ အလှဆင်ခြင်း ---
__author__   = 'maldevel'
__version__  = '2.0.4'

def Red(value): return colored(value, 'red', attrs=['bold'])
def Green(value): return colored(value, 'green', attrs=['bold'])

banner = f"""
{Red('IPGeolocation ' + __version__)}
{Red('--[')} Retrieve IP Geolocation information from ip-api.com
"""

# --- ၁။ Data Class ---
class IpGeoLocation:
    def __init__(self, query, jsonData=None):
        self.Query = query
        self.ASN = jsonData.get('as', '-')
        self.City = jsonData.get('city', '-')
        self.Country = jsonData.get('country', '-')
        self.CountryCode = jsonData.get('countryCode', '-')
        self.ISP = jsonData.get('isp', '-')
        self.Latitude = jsonData.get('lat', 0.0)
        self.Longitude = jsonData.get('lon', 0.0)
        self.IP = jsonData.get('query', '0.0.0.0')
        self.Timezone = jsonData.get('timezone', '-')
        self.GoogleMapsLink = f'https://www.google.com/maps/place/{self.Latitude},{self.Longitude}'

# --- ၂။ Logger Class ---
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

    def PrintResult(self, title, value):
        print(f"{title}: {Green(value)}")

    def PrintIPGeoLocation(self, obj):
        print(f"\n{Green('[+] Result for Target: ')}{obj.Query}")
        self.PrintResult("IP Address", obj.IP)
        self.PrintResult("Country", obj.Country)
        self.PrintResult("City", obj.City)
        self.PrintResult("ISP", obj.ISP)
        self.PrintResult("Location", f"{obj.Latitude}, {obj.Longitude}")
        self.PrintResult("Google Maps", obj.GoogleMapsLink)
        print()

# --- ၃။ Argument Check Functions ---
def checkFileRead(filename):
    if os.path.isfile(filename) and os.access(filename, os.R_OK):
        return filename
    raise argparse.ArgumentTypeError(f"Cannot read file: {filename}")

def checkProxyUrl(url):
    url_checked = urllib.parse.urlparse(url)
    if url_checked.scheme not in ('http', 'https') or url_checked.netloc == '':
        raise argparse.ArgumentTypeError(f"Invalid Proxy: {url}")
    return url

# --- ၄။ Core Logic ---
class IpGeoLocationLib:
    def __init__(self, logger):
        self.Logger = logger

    def GetInfo(self, target, open_maps=False, uagent=None):
        api_url = f"http://ip-api.com/json/{target}"
        headers = {'User-Agent': uagent or 'IPGeolocation/2.0.4'}
        
        try:
            self.Logger.Print(f"Querying information for: {target if target else 'Local IP'}")
            req = urllib.request.Request(api_url, headers=headers)
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
            
            if data['status'] == 'success':
                obj = IpGeoLocation(target or "MyIP", data)
                self.Logger.PrintIPGeoLocation(obj)
                if open_maps:
                    webbrowser.open(obj.GoogleMapsLink)
            else:
                self.Logger.PrintError(data['message'])
        except Exception as e:
            self.Logger.PrintError(str(e))

# --- ၅။ Main Program ---
def main():
    print(banner)
    parser = argparse.ArgumentParser(description="IP Geolocation Tool")
    parser.add_argument('-m', '--my-ip', action='store_true', help='Geolocation for my IP')
    parser.add_argument('-t', '--target', help='IP or Domain to analyze')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose')
    parser.add_argument('-g', action='store_true', help='Open in Google Maps')
    parser.add_argument('--nolog', action='store_true', help='Disable logging')
    parser.add_argument('-u', '--user-agent', help='Set custom User-Agent')

    args = parser.parse_args()
    logger = Logger(nolog=args.nolog, verbose=args.verbose)
    tool = IpGeoLocationLib(logger)

    if args.myip:
        tool.GetInfo("", open_maps=args.g, uagent=args.user_agent)
    elif args.target:
        # Hostname ကို IP ပြောင်းခြင်း
        try:
            target_ip = socket.gethostbyname(args.target)
            tool.GetInfo(target_ip, open_maps=args.g, uagent=args.user_agent)
        except:
            logger.PrintError("Could not resolve hostname.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()