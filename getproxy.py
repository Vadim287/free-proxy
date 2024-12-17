import json
import datetime
import requests
import re
import os
import subprocess
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed


class Downloadproxies():
    def __init__(self) -> None:
        self.api = {
            'socks4': [
                'https://raw.githubusercontent.com/ObcbO/getproxy/master/file/socks4.txt',
                'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt',
                'https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks4/socks4.txt',
                'https://raw.githubusercontent.com/ProxyScraper/ProxyScraper/main/socks4.txt',
                'https://raw.githubusercontent.com/TuanMinPay/live-proxy/master/socks4.txt',
                'https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks4.txt',
                'https://www.proxy-list.download/api/v1/get?type=socks4',
                'https://www.proxyscan.io/download?type=socks4',
                'https://spys.me/socks.txt',
                'https://www.my-proxy.com/socks-4.txt',
                'https://www.socks-proxy.net/',
                'https://proxyscrape.com/proxies/none_anonymous/socks4/file.txt',
                'https://www.proxy-list.download/SOCKS4',
                'https://txt.proxyspy.net/socks4.txt',
                'https://www.advanced.name/freeproxy/39543564f4ca9b7e56714fe23/',
                'https://hidemy.name/en/proxy-list/?type=4#list',
               
                'https://premproxy.com/socks-list/',
                'https://www.proxylists.net/',
                'https://www.sslproxies.org/',
                'https://www.freeproxylist.net/',
                'https://www.socks-proxy.net/',
                'https://www.socks24.org/',
               
            ],
            'socks5': [
                'https://raw.githubusercontent.com/ObcbO/getproxy/master/file/socks5.txt',
                'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',
                'https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt',
                'https://raw.githubusercontent.com/TuanMinPay/live-proxy/master/socks5.txt',
                'https://raw.githubusercontent.com/ProxyScraper/ProxyScraper/main/socks5.txt',
                'https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks5.txt',
                'https://www.proxy-list.download/api/v1/get?type=socks5',
                'https://www.proxyscan.io/download?type=socks5',
                'https://spys.me/socks.txt',
                'https://www.my-proxy.com/socks-5.txt',
                'https://proxyscrape.com/proxies/none_anonymous/socks5/file.txt',
                'https://www.proxy-list.download/SOCKS5',
                'https://www.socks-proxy.net/',
                'https://txt.proxyspy.net/socks5.txt',
                'https://www.advanced.name/freeproxy/8dec82dfe1c12b7de7f8f87ed/',
                'https://hidemy.name/en/proxy-list/?type=5#list',
               
                'https://sockslist.net/',
                'https://www.proxynova.com/proxy-server-list/socks5/',
                'https://www.socks-proxy.net/',
                'https://www.proxymanager.org/',
                'https://www.usaproxy.org/',
                
            ],
            'http': [
                'https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/https/https.txt',
                'https://raw.githubusercontent.com/ObcbO/getproxy/master/file/http.txt',
                'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
                'https://github.com/ObcbO/getproxy/blob/master/file/https.txt',
                'https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/http/http.txt',
                'https://raw.githubusercontent.com/TuanMinPay/live-proxy/master/http.txt',
                'https://raw.githubusercontent.com/ProxyScraper/ProxyScraper/main/http.txt',
                'https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt',
                'https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/https.txt',
                'https://www.proxy-list.download/api/v1/get?type=http',
                'https://www.proxyscan.io/download?type=http',
                'https://www.us-proxy.org/',
                'https://free-proxy-list.net/',
                'https://proxysearcher.sourceforge.net/Proxy%20List.php?type=http',
                'https://proxyscrape.com/proxies/none_anonymous/http/file.txt',
                'https://api.proxyscrape.com?request=getproxies&proxytype=http',
                'https://www.sslproxies.org/',
                'https://www.proxy-list.download/HTTP',
                'https://www.advanced.name/freeproxy/8dd96814aa62bca283294c051/',
                'https://www.xroxy.com/proxylist.php?port=&type=All_http&ssl=&country=&latency=&reliability=#table',
                
                'https://proxygather.com/',
                'https://www.proxynova.com/proxy-server-list/',
                'https://www.proxy-listen.de/Proxy/Proxyliste.html',
                'https://www.anonymous-proxy-servers.net/',
                'https://www.cool-proxy.net/',
                
            ]
        }
        self.proxy_dict = {'socks4': [], 'socks5': [], 'http': []}
        self.country_proxies = defaultdict(list)
        self.executor = ThreadPoolExecutor(max_workers=20000)  # Параллельная обработка

    def ip_to_country(self, ip):
        try:
            response = requests.get(f'http://ip-api.com/json/{ip}?fields=country', timeout=5)
            response.raise_for_status()
            data = response.json()
            return data.get('country', 'Unknown')
        except requests.RequestException:
            return 'Unknown'

    def sort_proxies_by_country(self):
        futures = []
        for proxy_type, proxies in self.proxy_dict.items():
            for proxy in proxies:
                ip = proxy.split(':')[0]
                futures.append(self.executor.submit(self.ip_to_country, ip))

        for future in as_completed(futures):
            country = future.result()
            if country != 'Unknown':
                self.country_proxies[country].append(proxy)

        print("Sorted proxies by country.")

    def get(self):
        futures = []
        for proxy_type, apis in self.api.items():
            for api in apis:
                futures.append(self.executor.submit(self.fetch_proxies, proxy_type, api))
    
        for future in as_completed(futures):
            try:
                future.result()  # Ждем, пока все запросы завершатся
            except Exception as e:
                 print(f"Error fetching proxies: {e}")

    # Вывод количества полученных прокси
        for proxy_type in self.proxy_dict:
            print(f"Total {proxy_type} proxies fetched: {len(self.proxy_dict[proxy_type])}")

        self.proxy_dict['socks4'] = list(set(self.proxy_dict['socks4']))
        self.proxy_dict['socks5'] = list(set(self.proxy_dict['socks5']))
        self.proxy_dict['http'] = list(set(self.proxy_dict['http']))

        print('> Get proxies done.')


    def fetch_proxies(self, proxy_type, api):
        try:
            r = requests.get(api, timeout=5)
            if r.status_code == 200:
                proxy_list = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}', r.text)
                self.proxy_dict[proxy_type].extend(proxy_list)
                print(f'> Get {len(proxy_list)} {proxy_type} ips from {api}')
        except requests.RequestException:
            pass

    def save_proxies_by_country(self):
        os.makedirs('world', exist_ok=True)
        for country, proxies in self.country_proxies.items():
            country_dir = os.path.join('world', country)
            os.makedirs(country_dir, exist_ok=True)
            with open(os.path.join(country_dir, 'proxies.txt'), 'w') as f:
                for proxy in proxies:
                    f.write(proxy + '\n')
            print(f"Saved proxies for {country} in {country_dir}")

    def execute(self):
        self.get()
        self.sort_proxies_by_country()
        self.save_proxies_by_country()

if __name__ == '__main__':
    d = Downloadproxies()
    d.execute()
