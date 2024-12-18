import asyncio
import aiohttp
import re
import os
from collections import defaultdict

class DownloadProxies:
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
        self.proxy_dict = defaultdict(set)
        self.country_proxies = defaultdict(list)
        self.semaphore = asyncio.Semaphore(100) 
        self.ip_country_cache = {}

    async def fetch_proxies(self, session, proxy_type, api):
        try:
            async with session.get(api, timeout=10) as response:
                if response.status == 200:
                    text = await response.text()
                    proxy_list = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}', text)
                    self.proxy_dict[proxy_type].update(proxy_list)
                    print(f'> Get {len(proxy_list)} {proxy_type} ips from {api}')
        except Exception as e:
            print(f"Error fetching from {api}: {e}")

    async def get_proxies(self):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for proxy_type, apis in self.api.items():
                for api in apis:
                    tasks.append(self.fetch_proxies(session, proxy_type, api))
            await asyncio.gather(*tasks)

       
        self.proxy_dict = {k: list(v) for k, v in self.proxy_dict.items()}
        for proxy_type in self.proxy_dict:
            print(f"Total {proxy_type} proxies fetched: {len(self.proxy_dict[proxy_type])}")

    async def ip_to_country(self, session, ip):
        if ip in self.ip_country_cache:
            return self.ip_country_cache[ip]
        try:
            async with self.semaphore:
                async with session.get(f'http://ip-api.com/json/{ip}?fields=country', timeout=5) as response:
                    data = await response.json()
                    country = data.get('country', 'Unknown')
                    self.ip_country_cache[ip] = country
                    return country
        except Exception:
            return 'Unknown'

    async def sort_proxies_by_country(self):
        async with aiohttp.ClientSession() as session:
            tasks = []
            unique_ips = set(proxy.split(':')[0] for proxies in self.proxy_dict.values() for proxy in proxies)
            for ip in unique_ips:
                tasks.append(self.ip_to_country(session, ip))
                    
            countries = await asyncio.gather(*tasks)

            ip_to_country_map = {ip: country for ip, country in zip(unique_ips, countries)}

            for proxy_type, proxies in self.proxy_dict.items():
                for proxy in proxies:
                    ip = proxy.split(':')[0]
                    country = ip_to_country_map[ip]
                    if country != 'Unknown':
                        self.country_proxies[country].append(proxy)

        print("Sorted proxies by country.")

    def save_proxies_by_country(self):
        os.makedirs('world', exist_ok=True)
        for country, proxies in self.country_proxies.items():
            country_dir = os.path.join('world', country)
            os.makedirs(country_dir, exist_ok=True)
            with open(os.path.join(country_dir, 'proxies.txt'), 'w') as f:
                for proxy in proxies:
                    f.write(proxy + '\n')
            print(f"Saved proxies for {country} in {country_dir}")

    def save_all_proxies(self):
        os.makedirs('proxies', exist_ok=True)

        file_paths = {
            'http': os.path.join('proxies', 'http.txt'),
            'socks4': os.path.join('proxies', 'socks4.txt'),
            'socks5': os.path.join('proxies', 'socks5.txt'),
            'all': os.path.join('proxies', 'all.txt')
        }

        with open(file_paths['all'], 'w') as all_file:
            for proxy_type, proxies in self.proxy_dict.items():
                with open(file_paths[proxy_type], 'w') as type_file:
                    for proxy in proxies:
                        type_file.write(proxy + '\n')
                        all_file.write(proxy + '\n')

        for proxy_type in file_paths:
            if proxy_type != 'all':
                print(f"Saved {proxy_type} proxies in {file_paths[proxy_type]}")
        print(f"Saved all proxies in {file_paths['all']}")

    async def execute(self):
        await self.get_proxies()
        await self.sort_proxies_by_country()
        self.save_proxies_by_country()
        self.save_all_proxies()

if __name__ == '__main__':
    d = DownloadProxies()
    asyncio.run(d.execute())
