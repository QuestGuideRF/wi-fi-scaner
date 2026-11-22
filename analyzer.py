from collections import defaultdict
class WiFiAnalyzer :
    CHANNEL_24GHZ =list (range (1 ,15 ))
    NON_OVERLAPPING_24 =[1 ,6 ,11 ]
    def __init__ (self ,database ):
        self .db =database
    def analyze_networks (self ,networks ):
        recommendations =[]
        issues =[]
        channel_analysis =self ._analyze_channels (networks )
        recommendations .extend (channel_analysis ['recommendations'])
        issues .extend (channel_analysis ['issues'])
        security_analysis =self ._analyze_security (networks )
        recommendations .extend (security_analysis ['recommendations'])
        issues .extend (security_analysis ['issues'])
        signal_analysis =self ._analyze_signal (networks )
        recommendations .extend (signal_analysis ['recommendations'])
        issues .extend (signal_analysis ['issues'])
        return {
        'recommendations':recommendations ,
        'issues':issues ,
        'channel_usage':channel_analysis ['usage'],
        'security_stats':security_analysis ['stats'],
        'signal_stats':signal_analysis ['stats']
        }
    def _analyze_channels (self ,networks ):
        channel_usage =defaultdict (list )
        for network in networks :
            channel =network .get ('channel',0 )
            if channel and channel in self .CHANNEL_24GHZ :
                channel_usage [channel ].append ({
                'ssid':network ['ssid'],
                'signal':network ['signal_strength']
                })
        recommendations =[]
        issues =[]
        for channel ,nets in channel_usage .items ():
            if len (nets )>5 :
                issues .append ({
                'type':'channel_congestion',
                'severity':'high'if len (nets )>10 else 'medium',
                'message':f'Канал {channel } перегружен ({len (nets )} сетей)',
                'channel':channel ,
                'count':len (nets )
                })
        if channel_usage :
            least_used =min (self .NON_OVERLAPPING_24 ,
            key =lambda ch :len (channel_usage .get (ch ,[])))
            current_usage =len (channel_usage .get (least_used ,[]))
            recommendations .append ({
            'type':'channel_optimization',
            'priority':'high',
            'message':f'Рекомендуется использовать канал {least_used } (загрузка: {current_usage } сетей)',
            'channel':least_used ,
            'reason':'Наименее загруженный непересекающийся канал'
            })
        recommendations .append ({
        'type':'channel_selection',
        'priority':'medium',
        'message':'Используйте каналы 1, 6 или 11 для минимизации помех',
        'reason':'Эти каналы не пересекаются в диапазоне 2.4 GHz'
        })
        return {
        'recommendations':recommendations ,
        'issues':issues ,
        'usage':dict (channel_usage )
        }
    def _analyze_security (self ,networks ):
        security_stats ={
        'high':0 ,
        'medium-high':0 ,
        'medium':0 ,
        'low':0 ,
        'none':0
        }
        recommendations =[]
        issues =[]
        insecure_networks =[]
        for network in networks :
            security_level =network .get ('security_level','Unknown').lower ()
            if security_level in security_stats :
                security_stats [security_level ]+=1
            if security_level in ['none','low']:
                insecure_networks .append (network ['ssid'])
                issues .append ({
                'type':'insecure_network',
                'severity':'high'if security_level =='none'else 'medium',
                'message':f'Сеть "{network ["ssid"]}" имеет низкий уровень безопасности',
                'ssid':network ['ssid'],
                'security':network .get ('security','Unknown')
                })
        if insecure_networks :
            recommendations .append ({
            'type':'security',
            'priority':'critical',
            'message':f'Обнаружено {len (insecure_networks )} небезопасных сетей. Избегайте подключения к открытым сетям',
            'affected_networks':insecure_networks [:5 ]
            })
        recommendations .append ({
        'type':'security',
        'priority':'high',
        'message':'Используйте сети с WPA2 или WPA3 шифрованием',
        'reason':'Обеспечивает защиту от несанкционированного доступа'
        })
        return {
        'recommendations':recommendations ,
        'issues':issues ,
        'stats':security_stats
        }
    def _analyze_signal (self ,networks ):
        signal_stats ={
        'excellent':0 ,
        'good':0 ,
        'fair':0 ,
        'weak':0 ,
        'very_weak':0
        }
        recommendations =[]
        issues =[]
        connected_network =None
        for network in networks :
            if network .get ('connected'):
                connected_network =network
            quality =network .get ('quality','Unknown').lower ().replace (' ','_')
            if quality in signal_stats :
                signal_stats [quality ]+=1
        if connected_network :
            signal =connected_network ['signal_strength']
            ssid =connected_network ['ssid']
            if signal <40 :
                issues .append ({
                'type':'weak_signal',
                'severity':'high'if signal <20 else 'medium',
                'message':f'Слабый сигнал подключенной сети "{ssid }" ({signal }%)',
                'ssid':ssid ,
                'signal':signal
                })
                recommendations .append ({
                'type':'signal_improvement',
                'priority':'high',
                'message':'Рекомендуется приблизиться к точке доступа или переставить роутер',
                'current_signal':signal ,
                'target_signal':'60%+'
                })
            elif signal >=80 :
                recommendations .append ({
                'type':'signal_status',
                'priority':'info',
                'message':f'Отличный сигнал сети "{ssid }" ({signal }%)',
                'status':'good'
                })
        if signal_stats ['weak']+signal_stats ['very_weak']>len (networks )*0.5 :
            recommendations .append ({
            'type':'signal_optimization',
            'priority':'medium',
            'message':'Большинство сетей имеют слабый сигнал. Проверьте расположение роутера',
            'weak_networks':signal_stats ['weak']+signal_stats ['very_weak'],
            'total_networks':len (networks )
            })
        return {
        'recommendations':recommendations ,
        'issues':issues ,
        'stats':signal_stats
        }
    def get_best_network (self ,networks ):
        secured_networks =[n for n in networks
        if n .get ('security_level','').lower ()not in ['none','low','unknown']]
        if not secured_networks :
            return None
        best_network =max (secured_networks ,key =lambda n :n .get ('signal_strength',0 ))
        return {
        'ssid':best_network ['ssid'],
        'signal':best_network ['signal_strength'],
        'security':best_network .get ('security','Unknown'),
        'channel':best_network .get ('channel',0 ),
        'reason':'Лучшее сочетание силы сигнала и безопасности'
        }