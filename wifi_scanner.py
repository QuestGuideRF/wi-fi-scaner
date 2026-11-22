import subprocess
import re
import platform
from datetime import datetime
import json
class WiFiScanner :
    def __init__ (self ):
        self .system =platform .system ()
    def scan_networks (self ):
        if self .system =="Windows":
            return self ._scan_windows ()
        elif self .system =="Linux":
            return self ._scan_linux ()
        elif self .system =="Darwin":
            return self ._scan_macos ()
        else :
            return []
    def _scan_windows (self ):
        networks =[]
        try :
            result =subprocess .check_output (
            ["netsh","wlan","show","networks","режим = Bssid"],
            encoding ='cp866',
            errors ='ignore'
            )
            current_network ={}
            bssid_count =0
            for line in result .split ('\n'):
                line =line .strip ()
                if line .startswith ('SSID'):
                    if current_network and 'ssid'in current_network :
                        networks .append (current_network .copy ())
                    ssid =line .split (':',1 )[1 ].strip ()
                    current_network ={
                    'ssid':ssid if ssid else f'Hidden Network {len (networks )}',
                    'timestamp':datetime .now ().isoformat ()
                    }
                    bssid_count =0
                elif 'Authentication'in line or 'Проверка подлинности'in line :
                    auth =line .split (':',1 )[1 ].strip ()
                    current_network ['security']=auth
                elif 'Encryption'in line or 'Шифрование'in line :
                    encryption =line .split (':',1 )[1 ].strip ()
                    current_network ['encryption']=encryption
                elif 'BSSID'in line :
                    bssid_count +=1
                    bssid =line .split (':',1 )[1 ].strip ()
                    if bssid_count ==1 :
                        current_network ['bssid']=bssid
                elif 'Signal'in line or 'Сигнал'in line :
                    signal =line .split (':',1 )[1 ].strip ().replace ('%','')
                    try :
                        current_network ['signal_strength']=int (signal )
                    except :
                        current_network ['signal_strength']=0
                elif 'Channel'in line or 'Канал'in line :
                    try :
                        channel =re .search (r'\d+',line .split (':',1 )[1 ])
                        if channel :
                            current_network ['channel']=int (channel .group ())
                    except :
                        pass
            if current_network and 'ssid'in current_network :
                networks .append (current_network )
            current_connection =self ._get_current_connection_windows ()
            for network in networks :
                if 'signal_strength'not in network :
                    network ['signal_strength']=0
                if 'channel'not in network :
                    network ['channel']=0
                if 'security'not in network :
                    network ['security']='Unknown'
                if 'bssid'not in network :
                    network ['bssid']='Unknown'
                network ['quality']=self ._get_signal_quality (network ['signal_strength'])
                network ['security_level']=self ._get_security_level (network .get ('security',''))
                network ['connected']=(current_connection and
                network ['ssid']==current_connection .get ('ssid'))
        except Exception as e :
            print (f"Error scanning networks: {e }")
        return networks
    def _scan_linux (self ):
        networks =[]
        try :
            result =subprocess .check_output (
            ["nmcli","-f","SSID, СИГНАЛ, ЧАН, БЕЗОПАСНОСТЬ, BSSID","dev","wifi"],
            encoding ='utf-8'
            )
            lines =result .split ('\n')[1 :]
            for line in lines :
                if line .strip ():
                    parts =line .split ()
                    if len (parts )>=4 :
                        networks .append ({
                        'ssid':parts [0 ],
                        'signal_strength':int (parts [1 ]),
                        'channel':int (parts [2 ])if parts [2 ].isdigit ()else 0 ,
                        'security':parts [3 ]if len (parts )>3 else 'Unknown',
                        'bssid':parts [4 ]if len (parts )>4 else 'Unknown',
                        'quality':self ._get_signal_quality (int (parts [1 ])),
                        'security_level':self ._get_security_level (parts [3 ]if len (parts )>3 else ''),
                        'timestamp':datetime .now ().isoformat (),
                        'connected':False
                        })
        except Exception as e :
            print (f"Error scanning networks (Linux): {e }")
        return networks
    def _scan_macos (self ):
        networks =[]
        try :
            result =subprocess .check_output (
            ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport","-s"],
            encoding ='utf-8'
            )
            lines =result .split ('\n')[1 :]
            for line in lines :
                if line .strip ():
                    parts =line .split ()
                    if len (parts )>=7 :
                        networks .append ({
                        'ssid':parts [0 ],
                        'bssid':parts [1 ],
                        'signal_strength':abs (int (parts [2 ])),
                        'channel':int (parts [3 ]),
                        'security':parts [6 ],
                        'quality':self ._get_signal_quality (abs (int (parts [2 ]))),
                        'security_level':self ._get_security_level (parts [6 ]),
                        'timestamp':datetime .now ().isoformat (),
                        'connected':False
                        })
        except Exception as e :
            print (f"Error scanning networks (macOS): {e }")
        return networks
    def _get_current_connection_windows (self ):
        try :
            result =subprocess .check_output (
            ["netsh","wlan","show","interfaces"],
            encoding ='cp866',
            errors ='ignore'
            )
            for line in result .split ('\n'):
                if 'SSID'in line and 'BSSID'not in line :
                    ssid =line .split (':',1 )[1 ].strip ()
                    return {'ssid':ssid }
        except :
            pass
        return None
    def _get_signal_quality (self ,signal_strength ):
        if signal_strength >=80 :
            return "Excellent"
        elif signal_strength >=60 :
            return "Good"
        elif signal_strength >=40 :
            return "Fair"
        elif signal_strength >=20 :
            return "Weak"
        else :
            return "Очень слабый"
    def _get_security_level (self ,security_type ):
        security_upper =security_type .upper ()
        if 'WPA3'in security_upper :
            return "High"
        elif 'WPA2'in security_upper :
            return "Medium-High"
        elif 'WPA'in security_upper :
            return "Medium"
        elif 'WEP'in security_upper :
            return "Low"
        elif 'OPEN'in security_upper or 'NONE'in security_upper or not security_type :
            return "None"
        else :
            return "Unknown"
    def get_connected_network_info (self ):
        if self .system =="Windows":
            return self ._get_connected_info_windows ()
        return None
    def _get_connected_info_windows (self ):
        try :
            result =subprocess .check_output (
            ["netsh","wlan","show","interfaces"],
            encoding ='cp866',
            errors ='ignore'
            )
            info ={}
            for line in result .split ('\n'):
                line =line .strip ()
                if ':'in line :
                    key ,value =line .split (':',1 )
                    key =key .strip ()
                    value =value .strip ()
                    if 'SSID'in key and 'BSSID'not in key :
                        info ['ssid']=value
                    elif 'BSSID'in key :
                        info ['bssid']=value
                    elif 'Signal'in key or 'Сигнал'in key :
                        try :
                            info ['signal']=int (value .replace ('%',''))
                        except :
                            pass
                    elif 'Channel'in key or 'Канал'in key :
                        try :
                            info ['channel']=int (value )
                        except :
                            pass
            return info if info else None
        except :
            return None