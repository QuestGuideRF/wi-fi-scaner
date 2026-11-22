import json
import os
from datetime import datetime ,timedelta
from collections import defaultdict
class WiFiDatabase :
    def __init__ (self ,db_file ='wifi_data.json'):
        self .db_file =db_file
        self .data =self ._load_data ()
    def _load_data (self ):
        if os .path .exists (self .db_file ):
            try :
                with open (self .db_file ,'r',encoding ='utf-8')as f :
                    return json .load (f )
            except :
                pass
        return {
        'scans':[],
        'connections':[],
        'networks':{}
        }
    def _save_data (self ):
        try :
            with open (self .db_file ,'w',encoding ='utf-8')as f :
                json .dump (self .data ,f ,ensure_ascii =False ,indent =2 )
        except Exception as e :
            print (f"Error saving data: {e }")
    def add_scan (self ,networks ):
        scan_data ={
        'timestamp':datetime .now ().isoformat (),
        'networks':networks ,
        'count':len (networks )
        }
        self .data ['scans'].append (scan_data )
        for network in networks :
            ssid =network ['ssid']
            if ssid not in self .data ['networks']:
                self .data ['networks'][ssid ]={
                'first_seen':scan_data ['timestamp'],
                'last_seen':scan_data ['timestamp'],
                'seen_count':1 ,
                'max_signal':network ['signal_strength'],
                'min_signal':network ['signal_strength'],
                'avg_signal':network ['signal_strength'],
                'channels':[network .get ('channel',0 )],
                'security':network .get ('security','Unknown'),
                'bssid':network .get ('bssid','Unknown')
                }
            else :
                net_info =self .data ['networks'][ssid ]
                net_info ['last_seen']=scan_data ['timestamp']
                net_info ['seen_count']+=1
                signal =network ['signal_strength']
                net_info ['max_signal']=max (net_info ['max_signal'],signal )
                net_info ['min_signal']=min (net_info ['min_signal'],signal )
                old_avg =net_info ['avg_signal']
                net_info ['avg_signal']=(old_avg *(net_info ['seen_count']-1 )+signal )/net_info ['seen_count']
                channel =network .get ('channel',0 )
                if channel and channel not in net_info ['channels']:
                    net_info ['channels'].append (channel )
        if len (self .data ['scans'])>1000 :
            self .data ['scans']=self .data ['scans'][-1000 :]
        self ._save_data ()
    def add_connection (self ,ssid ,connected =True ):
        connection_data ={
        'timestamp':datetime .now ().isoformat (),
        'ssid':ssid ,
        'event':'connected'if connected else 'disconnected'
        }
        self .data ['connections'].append (connection_data )
        if len (self .data ['connections'])>500 :
            self .data ['connections']=self .data ['connections'][-500 :]
        self ._save_data ()
    def get_recent_scans (self ,limit =10 ):
        return self .data ['scans'][-limit :]
    def get_network_history (self ,ssid ):
        if ssid in self .data ['networks']:
            return self .data ['networks'][ssid ]
        return None
    def get_all_networks (self ):
        return self .data ['networks']
    def get_connection_history (self ,hours =24 ):
        cutoff_time =datetime .now ()-timedelta (hours =hours )
        recent_connections =[]
        for conn in reversed (self .data ['connections']):
            try :
                conn_time =datetime .fromisoformat (conn ['timestamp'])
                if conn_time >=cutoff_time :
                    recent_connections .append (conn )
                else :
                    break
            except :
                pass
        return list (reversed (recent_connections ))
    def get_channel_usage (self ):
        channel_usage =defaultdict (list )
        if self .data ['scans']:
            latest_scan =self .data ['scans'][-1 ]
            for network in latest_scan ['networks']:
                channel =network .get ('channel',0 )
                if channel :
                    channel_usage [channel ].append ({
                    'ssid':network ['ssid'],
                    'signal':network ['signal_strength']
                    })
        return dict (channel_usage )
    def get_statistics (self ):
        stats ={
        'total_scans':len (self .data ['scans']),
        'total_networks_seen':len (self .data ['networks']),
        'total_connections':len (self .data ['connections']),
        'current_networks':0
        }
        if self .data ['scans']:
            stats ['current_networks']=self .data ['scans'][-1 ]['count']
        return stats
    def get_signal_history (self ,ssid ,hours =24 ):
        cutoff_time =datetime .now ()-timedelta (hours =hours )
        history =[]
        for scan in self .data ['scans']:
            try :
                scan_time =datetime .fromisoformat (scan ['timestamp'])
                if scan_time >=cutoff_time :
                    for network in scan ['networks']:
                        if network ['ssid']==ssid :
                            history .append ({
                            'timestamp':scan ['timestamp'],
                            'signal':network ['signal_strength']
                            })
                            break
            except :
                pass
        return history