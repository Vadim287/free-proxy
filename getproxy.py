import asyncio
import aiohttp
import re
import os
import sys
from collections import defaultdict
import geoip2.database
from bs4 import BeautifulSoup
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('download_proxies.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

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
                'https://raw.githubusercontent.com/ObcbO/getproxy/raw/master/file/https.txt',
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
       
        self.semaphore = asyncio.Semaphore(500)
        self.ip_country_cache = {}
        self.geoip_readers = self.setup_geoip()

    def setup_geoip(self):
        geoip_db_paths = {
            'country': 'GeoLite2-Country.mmdb',
            'city': 'GeoLite2-City.mmdb',
            'asn': 'GeoLite2-ASN.mmdb'
        }
        download_urls = {
            'country': [
                'https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-Country.mmdb',
                'https://git.io/GeoLite2-Country.mmdb'
            ],
            'city': [
                'https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-City.mmdb',
                'https://git.io/GeoLite2-City.mmdb'
            ],
            'asn': [
                'https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-ASN.mmdb',
                'https://git.io/GeoLite2-ASN.mmdb'
            ]
        }
        readers = {}
        for key, path in geoip_db_paths.items():
            if not os.path.exists(path):
                logger.info(f"Файл {path} не найден. Начало скачивания.")
                success = self.download_geoip_database(key, path, download_urls[key])
                if not success:
                    logger.error(f"Не удалось скачать {path}. Завершение работы.")
                    sys.exit(1)
            try:
                readers[key] = geoip2.database.Reader(path)
                logger.info(f"Загружен {key} GeoIP database из {path}.")
            except Exception as e:
                logger.error(f"Ошибка загрузки {path}: {e}")
                sys.exit(1)
        return readers

    def download_geoip_database(self, key, path, urls):
        for url in urls:
            try:
                logger.info(f"Попытка скачать {path} с {url}")
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    with open(path, 'wb') as f:
                        f.write(response.content)
                    logger.info(f"Успешно скачан {path} с {url}")
                    return True
                else:
                    logger.warning(f"Не удалось скачать {path} с {url}. Статус код: {response.status_code}")
            except Exception as e:
                logger.warning(f"Ошибка при скачивании {path} с {url}: {e}")
        return False

    async def fetch_proxies(self, session, proxy_type, api):
        try:
            async with self.semaphore:
                async with session.get(api, timeout=15) as response:
                    if response.status == 200:
                        if any(domain in api for domain in ['spys.me', 'hidemy.name', 'proxynova.com', 'proxy-listen.de']):
                            # Обработка HTML-страниц
                            text = await response.text()
                            proxy_list = self.parse_html_proxies(text)
                        else:
                            text = await response.text()
                            proxy_list = re.findall(r'\d{1,3}(?:\.\d{1,3}){3}:\d{2,5}', text)
                        if proxy_list:
                            self.proxy_dict[proxy_type].update(proxy_list)
                            logger.info(f"> Получено {len(proxy_list)} {proxy_type.upper()} прокси из {api}")
        except Exception as e:
            logger.error(f"Ошибка при загрузке из {api}: {e}")

    def parse_html_proxies(self, html_text):
        proxies = []
        try:
            soup = BeautifulSoup(html_text, 'html.parser')
            # Пример для сайтов с таблицей прокси
            for row in soup.find_all('tr'):
                cols = row.find_all(['td', 'li'])
                if cols:
                    for col in cols:
                        proxy = col.get_text(strip=True)
                        if re.match(r'\d{1,3}(?:\.\d{1,3}){3}:\d{2,5}', proxy):
                            proxies.append(proxy)
        except Exception as e:
            logger.error(f"Ошибка при парсинге HTML: {e}")
        return proxies

    async def get_proxies(self):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for proxy_type, apis in self.api.items():
                for api in apis:
                    tasks.append(self.fetch_proxies(session, proxy_type, api))
            await asyncio.gather(*tasks)

        # Преобразование сетов в списки
        self.proxy_dict = {k: list(v) for k, v in self.proxy_dict.items()}
        for proxy_type in self.proxy_dict:
            logger.info(f"Всего {proxy_type.upper()} прокси получено: {len(self.proxy_dict[proxy_type])}")

    def ip_to_country_local(self, ip):
        try:
            response = self.geoip_readers['country'].country(ip)
            country = response.country.name or 'Unknown'
            return country
        except Exception:
            return 'Unknown'

    def ip_to_city_local(self, ip):
        try:
            response = self.geoip_readers['city'].city(ip)
            city = response.city.name or 'Unknown'
            return city
        except Exception:
            return 'Unknown'

    def ip_to_asn_local(self, ip):
        try:
            response = self.geoip_readers['asn'].asn(ip)
            asn = response.autonomous_system_organization or 'Unknown'
            return asn
        except Exception:
            return 'Unknown'

    async def sort_proxies_by_country(self):
        loop = asyncio.get_event_loop()
        unique_ips = set(proxy.split(':')[0] for proxies in self.proxy_dict.values() for proxy in proxies)
        ip_to_country_map = {}

        tasks = [loop.run_in_executor(None, self.ip_to_country_local, ip) for ip in unique_ips]
        countries = await asyncio.gather(*tasks)

        ip_to_country_map = {ip: country for ip, country in zip(unique_ips, countries)}

        for proxy_type, proxies in self.proxy_dict.items():
            for proxy in proxies:
                ip, port = proxy.split(':')
                country = ip_to_country_map.get(ip, 'Unknown')
                if country != 'Unknown':
                    # Сохраняем кортеж (протокол, прокси)
                    self.country_proxies[country].append((proxy_type, proxy))

        logger.info("Прокси отсортированы по странам.")

    def save_proxies_by_country(self):
        os.makedirs('world', exist_ok=True)
        for country, proxies in self.country_proxies.items():
            safe_country = re.sub(r'[\\/*?:"<>|]', "_", country)
            country_dir = os.path.join('world', safe_country)
            os.makedirs(country_dir, exist_ok=True)
            file_path = os.path.join(country_dir, 'proxies.txt')
            try:
                with open(file_path, 'w') as f:
                    for proxy_type, proxy in proxies:
                        f.write(f"{proxy_type.upper()} {proxy}\n")
                logger.info(f"Сохранены прокси для {country} в {country_dir}")
            except Exception as e:
                logger.error(f"Ошибка при сохранении прокси для {country}: {e}")

    def save_all_proxies(self):
        os.makedirs('proxies', exist_ok=True)

        file_paths = {
            'http': os.path.join('proxies', 'http.txt'),
            'socks4': os.path.join('proxies', 'socks4.txt'),
            'socks5': os.path.join('proxies', 'socks5.txt'),
            'all': os.path.join('proxies', 'all.txt')
        }

      
        for proxy_type, proxies in self.proxy_dict.items():
            try:
                with open(file_paths[proxy_type], 'w') as type_file:
                    type_file.write('\n'.join(proxies))
                logger.info(f"Сохранены {proxy_type.upper()} прокси в {file_paths[proxy_type]}")
            except Exception as e:
                logger.error(f"Ошибка при сохранении {proxy_type.upper()} прокси: {e}")

       
        all_proxies = set()
        for proxies in self.proxy_dict.values():
            all_proxies.update(proxies)
        try:
            with open(file_paths['all'], 'w') as all_file:
                all_file.write('\n'.join(all_proxies))
            logger.info(f"Сохранены все прокси в {file_paths['all']}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении всех прокси: {e}")

    async def validate_proxy(self, session, proxy):
        test_url = 'http://www.google.com'
        try:
            async with session.get(test_url, proxy=f'http://{proxy}', timeout=5):
                return True
        except:
            return False

    async def validate_single_proxy(self, session, proxy_type, proxy):
        is_valid = await self.validate_proxy(session, proxy)
        return proxy_type, proxy, is_valid

    async def validate_proxies(self):
        valid_proxies = defaultdict(set)
        async with aiohttp.ClientSession() as session:
            tasks = []
            for proxy_type, proxies in self.proxy_dict.items():
                for proxy in proxies:
                    tasks.append(self.validate_single_proxy(session, proxy_type, proxy))
            results = await asyncio.gather(*tasks)
            for proxy_type, proxy, is_valid in results:
                if is_valid:
                    valid_proxies[proxy_type].add(proxy)
        self.proxy_dict = valid_proxies
        logger.info("Валидация прокси завершена.")

    async def execute(self):
        logger.info("Начало загрузки прокси...")
        await self.get_proxies()
        logger.info("Загрузка прокси завершена.")

        logger.info("Начало сортировки прокси по странам...")
        await self.sort_proxies_by_country()

        logger.info("Начало валидации прокси...")
        await self.validate_proxies()

        logger.info("Сортировка и валидация прокси завершены.")

        logger.info("Начало сохранения прокси по странам...")
        self.save_proxies_by_country()

        logger.info("Начало сохранения всех прокси...")
        self.save_all_proxies()

        logger.info("Все операции завершены.")

    def close(self):
        for reader in self.geoip_readers.values():
            reader.close()

if __name__ == '__main__':
    import requests  

    d = DownloadProxies()
    try:
        asyncio.run(d.execute())
    finally:
        d.close()
