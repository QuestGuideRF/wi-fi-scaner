from flask import Flask ,jsonify ,render_template ,send_from_directory ,request
from flask_cors import CORS
from datetime import datetime
import threading
import time
import os
from wifi_scanner import WiFiScanner
from database import WiFiDatabase
from analyzer import WiFiAnalyzer
app =Flask (__name__ ,static_folder ='static',template_folder ='templates')
CORS (app )
scanner =WiFiScanner ()
db =WiFiDatabase ()
analyzer =WiFiAnalyzer (db )
current_scan_data =None
scan_in_progress =False
auto_scan_enabled =True
auto_scan_interval =30
def auto_scan_worker ():
    global current_scan_data ,scan_in_progress
    while True :
        if auto_scan_enabled :
            try :
                scan_in_progress =True
                networks =scanner .scan_networks ()
                if networks :
                    db .add_scan (networks )
                    current_scan_data ={
                    'timestamp':datetime .now ().isoformat (),
                    'networks':networks ,
                    'count':len (networks )
                    }
                    connected_info =scanner .get_connected_network_info ()
                    if connected_info :
                        for network in networks :
                            if network ['ssid']==connected_info .get ('ssid'):
                                network ['connected']=True
                scan_in_progress =False
            except Exception as e :
                print (f"Auto scan error: {e }")
                scan_in_progress =False
        time .sleep (auto_scan_interval )
scan_thread =threading .Thread (target =auto_scan_worker ,daemon =True )
scan_thread .start ()
@app .route ('/')
def index ():
    return render_template ('index.html')
@app .route ('/api/scan')
def api_scan ():
    global current_scan_data ,scan_in_progress
    if scan_in_progress :
        return jsonify ({
        'status':'scanning',
        'message':'Сканирование уже выполняется'
        }),202
    try :
        scan_in_progress =True
        networks =scanner .scan_networks ()
        if networks :
            db .add_scan (networks )
            current_scan_data ={
            'timestamp':datetime .now ().isoformat (),
            'networks':networks ,
            'count':len (networks )
            }
        scan_in_progress =False
        return jsonify ({
        'status':'success',
        'data':current_scan_data
        })
    except Exception as e :
        scan_in_progress =False
        return jsonify ({
        'status':'error',
        'message':str (e )
        }),500
@app .route ('/api/current')
def api_current ():
    if current_scan_data :
        return jsonify ({
        'status':'success',
        'data':current_scan_data ,
        'scanning':scan_in_progress
        })
    else :
        return jsonify ({
        'status':'no_data',
        'message':'Нет данных. Ожидайте первого сканирования',
        'scanning':scan_in_progress
        })
@app .route ('/api/analysis')
def api_analysis ():
    if not current_scan_data :
        return jsonify ({
        'status':'no_data',
        'message':'Нет данных для анализа'
        })
    try :
        analysis =analyzer .analyze_networks (current_scan_data ['networks'])
        best_network =analyzer .get_best_network (current_scan_data ['networks'])
        return jsonify ({
        'status':'success',
        'data':{
        'analysis':analysis ,
        'best_network':best_network
        }
        })
    except Exception as e :
        return jsonify ({
        'status':'error',
        'message':str (e )
        }),500
@app .route ('/api/channel-usage')
def api_channel_usage ():
    channel_usage =db .get_channel_usage ()
    channels =[]
    counts =[]
    for channel in range (1 ,15 ):
        channels .append (channel )
        counts .append (len (channel_usage .get (channel ,[])))
    return jsonify ({
    'status':'success',
    'data':{
    'channels':channels ,
    'counts':counts ,
    'details':channel_usage
    }
    })
@app .route ('/api/signal-history/<ssid>')
def api_signal_history (ssid ):
    hours =24
    history =db .get_signal_history (ssid ,hours )
    return jsonify ({
    'status':'success',
    'data':{
    'ssid':ssid ,
    'history':history ,
    'hours':hours
    }
    })
@app .route ('/api/network-history/<ssid>')
def api_network_history (ssid ):
    history =db .get_network_history (ssid )
    if history :
        return jsonify ({
        'status':'success',
        'data':history
        })
    else :
        return jsonify ({
        'status':'not_found',
        'message':'Сеть не найдена в истории'
        }),404
@app .route ('/api/connections')
def api_connections ():
    hours =int (request .args .get ('hours',24 ))
    connections =db .get_connection_history (hours )
    return jsonify ({
    'status':'success',
    'data':{
    'connections':connections ,
    'hours':hours
    }
    })
@app .route ('/api/statistics')
def api_statistics ():
    stats =db .get_statistics ()
    return jsonify ({
    'status':'success',
    'data':stats
    })
@app .route ('/api/settings',methods =['GET','POST'])
def api_settings ():
    global auto_scan_enabled ,auto_scan_interval
    if request .method =='POST':
        data =request .get_json ()
        if 'enabled'in data :
            auto_scan_enabled =data ['enabled']
        if 'interval'in data :
            auto_scan_interval =max (5 ,int (data ['interval']))
        return jsonify ({
        'status':'success',
        'message':'Настройки обновлены'
        })
    else :
        return jsonify ({
        'status':'success',
        'data':{
        'auto_scan_enabled':auto_scan_enabled ,
        'auto_scan_interval':auto_scan_interval
        }
        })
@app .route ('/api/all-networks')
def api_all_networks ():
    networks =db .get_all_networks ()
    return jsonify ({
    'status':'success',
    'data':{
    'networks':networks ,
    'count':len (networks )
    }
    })
if __name__ =='__main__':
    os .makedirs ('static',exist_ok =True )
    os .makedirs ('templates',exist_ok =True )
    print ("="*60 )
    print ("WiFi Monitor - Система мониторинга WiFi сетей")
    print ("="*60 )
    print ("\nСервер запускается на http://localhost:5000")
    print ("Откройте браузер и перейдите по этому адресу\n")
    print ("Автоматическое сканирование: каждые",auto_scan_interval ,"секунд")
    print ("="*60 )
    app .run (debug =True ,host ='0.0.0.0',port =5000 ,use_reloader =False )