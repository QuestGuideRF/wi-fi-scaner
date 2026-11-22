import requests
import time
import json
BASE_URL ='http://localhost:5000'
def print_section (title ):
    print ("\n"+"="*60 )
    print (f"  {title }")
    print ("="*60 )
def demo_scan ():
    print_section ("1. СКАНИРОВАНИЕ WIFI СЕТЕЙ")
    response =requests .get (f'{BASE_URL }/api/scan')
    data =response .json ()
    if data ['status']=='success':
        networks =data ['data']['networks']
        print (f"✓ Обнаружено сетей: {len (networks )}")
        top_networks =sorted (networks ,key =lambda x :x ['signal_strength'],reverse =True )[:3 ]
        print ("\nТоп-3 сети по сигналу:")
        for i ,net in enumerate (top_networks ,1 ):
            print (f"  {i }. {net ['ssid']}: {net ['signal_strength']}% (Канал {net .get ('channel','N/A')})")
    else :
        print (f"✗ Ошибка: {data .get ('message','Неизвестная ошибка')}")
def demo_analysis ():
    print_section ("2. АНАЛИЗ И РЕКОМЕНДАЦИИ")
    response =requests .get (f'{BASE_URL }/api/analysis')
    data =response .json ()
    if data ['status']=='success':
        analysis =data ['data']['analysis']
        best_network =data ['data']['best_network']
        print (f"✓ Рекомендаций: {len (analysis ['recommendations'])}")
        print (f"✓ Проблем обнаружено: {len (analysis ['issues'])}")
        if analysis ['recommendations']:
            print ("\nВажные рекомендации:")
            for rec in analysis ['recommendations'][:3 ]:
                print (f"  • {rec ['message']}")
        if best_network :
            print (f"\n🏆 Рекомендуемая сеть: {best_network ['ssid']}")
            print (f"   Сигнал: {best_network ['signal']}%")
            print (f"   Безопасность: {best_network ['security']}")
def demo_channels ():
    print_section ("3. ЗАГРУЗКА КАНАЛОВ")
    response =requests .get (f'{BASE_URL }/api/channel-usage')
    data =response .json ()
    if data ['status']=='success':
        channels =data ['data']['channels']
        counts =data ['data']['counts']
        print ("Использование каналов 2.4 GHz:")
        for ch ,count in zip (channels ,counts ):
            if count >0 :
                bar ='█'*count
                print (f"  Канал {ch :2d}: {bar } ({count })")
def demo_statistics ():
    print_section ("4. ОБЩАЯ СТАТИСТИКА")
    response =requests .get (f'{BASE_URL }/api/statistics')
    data =response .json ()
    if data ['status']=='success':
        stats =data ['data']
        print (f"  Всего сканирований: {stats ['total_scans']}")
        print (f"  Всего сетей обнаружено: {stats ['total_networks_seen']}")
        print (f"  Текущих сетей: {stats ['current_networks']}")
        print (f"  Записей о подключениях: {stats ['total_connections']}")
def main ():
    print ("\n"+"🛜 "*20 )
    print ("  WiFi МОНИТОР — ДЕМО API")
    print ("🛜 "*20 )
    try :
        response =requests .get (BASE_URL ,timeout =2 )
        if response .status_code !=200 :
            print ("\n✗ Сервер недоступен. Запустите: python app.py")
            return
    except :
        print ("\n✗ Сервер недоступен. Запустите: python app.py")
        return
    print ("\n✓ Сервер доступен")
    demo_scan ()
    time .sleep (1 )
    demo_analysis ()
    time .sleep (1 )
    demo_channels ()
    time .sleep (1 )
    demo_statistics ()
    print_section ("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print ("\n📊 Откройте http://localhost:5000 для просмотра веб-дашборда\n")
if __name__ =='__main__':
    main ()