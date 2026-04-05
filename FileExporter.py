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
import csv
from datetime import datetime
from xml.etree import ElementTree as etree
from collections import OrderedDict
from termcolor import colored
from sys import platform as _platform

# Windows အရောင်စနစ်
if _platform == 'win32':
    import colorama
    colorama.init()

# --- ၁။ Logger & Colors ---
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

    def PrintIPGeoLocation(self, obj):
        print(f"\n{Green('[+] Result for: ')}{obj.Query}")
        print(f"    IP Address    : {obj.IP}")
        print(f"    Country       : {obj.Country}")
        print(f"    ISP           : {obj.ISP}")
        print(f"    Location      : {obj.Latitude}, {obj.Longtitude}")
        print(f"    Google Maps   : {obj.GoogleMapsLink}")
        print("-" * 50)

# --- ၂။ Data Class ---
class IpGeoLocation:
    def __init__(self, query, jsonData):
        self.Query = query
        self.IP = jsonData.get('query', '-')
        self.ASN = jsonData.get('as', '-')
        self.City = jsonData.get('city', '-')
        self.Country = jsonData.get('country', '-')
        self.CountryCode = jsonData.get('countryCode', '-')
        self.ISP = jsonData.get('isp', '-')
        self.Latitude = jsonData.get('lat', 0.0)
        self.Longtitude = jsonData.get('lon', 0.0) # User spelling
        self.Organization = jsonData.get('org', '-')
        self.Region = jsonData.get('region', '-')
        self.RegionName = jsonData.get('regionName', '-')
        self.Timezone = jsonData.get('timezone', '-')
        self.Zip = jsonData.get('zip', '-')
        self.GoogleMapsLink = f"https://www.google.com/maps/place/{self.Latitude},{self.Longtitude}"

    def ToDict(self):
        return {
            'Target': self.Query, 'IP': self.IP, 'ASN': self.ASN, 'City': self.City,
            'Country': self.Country, 'ISP': self.ISP, 'Latitude': str(self.Latitude),
            'Longitude': str(self.Longtitude), 'Timezone': self.Timezone, 'GoogleMaps': self.GoogleMapsLink
        }

# --- ၃။ File Exporter Class ---
class FileExporter:
    def ExportToCSV(self, obj, filename):
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(['Field', 'Value'])
                for k, v in obj.ToDict().items():
                    writer.writerow([k, v])
            return True
        except: return False

    def ExportToJSON(self, obj, filename):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(obj.ToDict(), f, indent=4)
            return True
        except: return False

    def ExportToTXT(self, obj, filename):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for k, v in obj.ToDict().items():
                    f.write(f"{k}: {v}\n")
            return True
        except: return False

# --- ၄။ Main Logic ---
class IpGeoLocationLib:
    def __init__(self, logger):
        self.Logger = logger
        self.Exporter = FileExporter()

    def GetInfo(self, target, args):
        api_url = f"http://ip-api.com/json/{target}"
        try:
            req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())

            if data['status'] == 'success':
                obj = IpGeoLocation(target if target else "MyIP", data)
                self.Logger.PrintIPGeoLocation(obj)

                # Exporting
                if args.txt: 
                    if self.Exporter.ExportToTXT(obj, args.txt): self.Logger.Print(f"Saved to {args.txt}")
                if args.csv:
                    if self.Exporter.ExportToCSV(obj, args.csv): self.Logger.Print(f"Saved to {args.csv}")
                if args.json:
                    if self.Exporter.ExportToJSON(obj, args.json): self.Logger.Print(f"Saved to {args.json}")
                
                if args.g: webbrowser.open(obj.GoogleMapsLink)
            else:
                self.Logger.PrintError(data['message'])
        except Exception as e:
            self.Logger.PrintError(str(e))

# --- ၅။ Program Entry ---
def main():
    print(Yellow("IP Geolocation Tool v2.0 - Final Real Version"))
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--target', help='Target IP or Domain')
    parser.add_argument('-m', '--my-ip', action='store_true', help='My IP Geolocation')
    parser.add_argument('-g', action='store_true', help='Open in Google Maps')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
    parser.add_argument('--txt', metavar='file', help='Export to TXT')
    parser.add_argument('--csv', metavar='file', help='Export to CSV')
    parser.add_argument('--json', metavar='file', help='Export to JSON')

    args = parser.parse_args()
    logger = Logger(verbose=args.verbose)
    tool = IpGeoLocationLib(logger)

    if args.my_ip: tool.GetInfo("", args)
    elif args.target:
        try:
            ip = socket.gethostbyname(args.target)
            tool.GetInfo(ip, args)
        except: logger.PrintError("Invalid Target")
    else: parser.print_help()

if __name__ == "__main__":
    main()