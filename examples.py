import requests
response =requests .get ('http://localhost:5000/api/scan')
data =response .json ()
print (f"Найдено сетей: {data ['data']['count']}")
response =requests .get ('http://localhost:5000/api/current')
networks =response .json ()['data']['networks']
for net in networks :
    print (f"{net ['ssid']}: {net ['signal_strength']}%")
response =requests .get ('http://localhost:5000/api/analysis')
analysis =response .json ()['data']
for rec in analysis ['analysis']['recommendations']:
    print (f"💡 {rec ['message']}")
for issue in analysis ['analysis']['issues']:
    print (f"⚠️ {issue ['message']}")
best =analysis ['best_network']
if best :
    print (f"🏆 Рекомендуется: {best ['ssid']} ({best ['signal']}%)")
ssid ="MyNetwork"
response =requests .get (f'http://localhost:5000/api/network-history/{ssid }')
history =response .json ()['data']
print (f"Сеть {ssid }:")
print (f"  Впервые видели: {history ['first_seen']}")
print (f"  Видели раз: {history ['seen_count']}")
print (f"  Средний сигнал: {history ['avg_signal']:.1f}%")
response =requests .get ('http://localhost:5000/api/statistics')
stats =response .json ()['data']
print (f"\nВсего сканирований: {stats ['total_scans']}")
print (f"Уникальных сетей: {stats ['total_networks_seen']}")
from wifi_scanner import WiFiScanner
from database import WiFiDatabase
from analyzer import WiFiAnalyzer
scanner =WiFiScanner ()
db =WiFiDatabase ()
analyzer =WiFiAnalyzer (db )
networks =scanner .scan_networks ()
print (f"Обнаружено: {len (networks )} сетей")
db .add_scan (networks )
analysis =analyzer .analyze_networks (networks )
print (f"Рекомендаций: {len (analysis ['recommendations'])}")
print (f"Проблем: {len (analysis ['issues'])}")
best =analyzer .get_best_network (networks )
if best :
    print (f"Лучшая сеть: {best ['ssid']}")
import time
def monitor_wifi (duration_minutes =5 ):
    start_time =time .time ()
    end_time =start_time +(duration_minutes *60 )
    while time .time ()<end_time :
        response =requests .get ('http://localhost:5000/api/current')
        data =response .json ()
        if data ['status']=='success':
            networks =data ['data']['networks']
            timestamp =data ['data']['timestamp']
            print (f"\n[{timestamp }]")
            print (f"Сетей: {len (networks )}")
            top =sorted (networks ,key =lambda x :x ['signal_strength'],reverse =True )[:3 ]
            for i ,net in enumerate (top ,1 ):
                print (f"  {i }. {net ['ssid']}: {net ['signal_strength']}%")
        time .sleep (30 )
import json
import csv
def export_to_json (filename ='wifi_export.json'):
    response =requests .get ('http://localhost:5000/api/all-networks')
    data =response .json ()['data']
    with open (filename ,'w',encoding ='utf-8')as f :
        json .dump (data ,f ,ensure_ascii =False ,indent =2 )
    print (f"Экспортировано в {filename }")
def export_to_csv (filename ='wifi_export.csv'):
    response =requests .get ('http://localhost:5000/api/current')
    networks =response .json ()['data']['networks']
    with open (filename ,'w',newline ='',encoding ='utf-8')as f :
        writer =csv .DictWriter (f ,fieldnames =['ssid','signal_strength','channel','security','bssid'])
        writer .writeheader ()
        for net in networks :
            writer .writerow ({
            'ssid':net ['ssid'],
            'signal_strength':net ['signal_strength'],
            'channel':net .get ('channel',''),
            'security':net .get ('security',''),
            'bssid':net .get ('bssid','')
            })
    print (f"Экспортировано в {filename }")
def find_best_channel ():
    response =requests .get ('http://localhost:5000/api/channel-usage')
    data =response .json ()['data']
    channels =data ['channels']
    counts =data ['counts']
    recommended_channels ={1 :0 ,6 :0 ,11 :0 }
    for ch ,count in zip (channels ,counts ):
        if ch in recommended_channels :
            recommended_channels [ch ]=count
    best_channel =min (recommended_channels .items (),key =lambda x :x [1 ])
    print (f"Рекомендуемый канал: {best_channel [0 ]}")
    print (f"Загрузка: {best_channel [1 ]} сетей")
    print ("\nЗагрузка непересекающихся каналов:")
    for ch ,count in recommended_channels .items ():
        print (f"  Канал {ch }: {count } сетей")
    return best_channel [0 ]
def track_signal_changes (ssid ,duration_minutes =10 ):
    import matplotlib .pyplot as plt
    from datetime import datetime
    timestamps =[]
    signals =[]
    start_time =time .time ()
    end_time =start_time +(duration_minutes *60 )
    while time .time ()<end_time :
        response =requests .get ('http://localhost:5000/api/current')
        data =response .json ()
        if data ['status']=='success':
            networks =data ['data']['networks']
            for net in networks :
                if net ['ssid']==ssid :
                    timestamps .append (datetime .now ())
                    signals .append (net ['signal_strength'])
                    print (f"[{datetime .now ().strftime ('%H:%M:%S')}] {ssid }: {net ['signal_strength']}%")
                    break
        time .sleep (10 )
    if timestamps and signals :
        plt .figure (figsize =(12 ,6 ))
        plt .plot (timestamps ,signals ,marker ='o')
        plt .title (f'Сила сигнала: {ssid }')
        plt .xlabel ('Время')
        plt .ylabel ('Сигнал (%)')
        plt .grid (True )
        plt .xticks (rotation =45 )
        plt .tight_layout ()
        plt .savefig (f'signal_{ssid }.png')
        print (f"\nГрафик сохранен: signal_{ssid }.png")
def check_network_security ():
    response =requests .get ('http://localhost:5000/api/current')
    networks =response .json ()['data']['networks']
    security_levels ={
    'secure':[],
    'moderate':[],
    'insecure':[]
    }
    for net in networks :
        level =net .get ('security_level','').lower ()
        ssid =net ['ssid']
        if level in ['high','medium-high']:
            security_levels ['secure'].append (ssid )
        elif level =='medium':
            security_levels ['moderate'].append (ssid )
        else :
            security_levels ['insecure'].append (ssid )
    print ("🔒 БЕЗОПАСНЫЕ СЕТИ:")
    for ssid in security_levels ['secure']:
        print (f"  ✓ {ssid }")
    print ("\n⚠️ СРЕДНЯЯ БЕЗОПАСНОСТЬ:")
    for ssid in security_levels ['moderate']:
        print (f"  ⚠ {ssid }")
    print ("\n❌ НЕБЕЗОПАСНЫЕ СЕТИ:")
    for ssid in security_levels ['insecure']:
        print (f"  ✗ {ssid }")
    return security_levels
def check_and_notify ():
    response =requests .get ('http://localhost:5000/api/analysis')
    data =response .json ()['data']
    issues =data ['analysis']['issues']
    critical_issues =[i for i in issues if i .get ('severity')=='high']
    if critical_issues :
        print ("🚨 КРИТИЧЕСКИЕ ПРОБЛЕМЫ:")
        for issue in critical_issues :
            print (f"  • {issue ['message']}")
    else :
        print ("✅ Критических проблем не обнаружено")