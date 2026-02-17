#!/usr/bin/env python3
"""
AccBlox Product Monitor
Monitors accblox.net for target product and sends Telegram alerts
"""

import requests
import json
import time
import logging
from datetime import datetime
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor.log'),
        logging.StreamHandler()
    ]
)

class AccBloxMonitor:
    def __init__(self, config_path='config.json'):
        """Initialize monitor with configuration"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.telegram_token = self.config['telegram_bot_token']
        self.telegram_chat_id = self.config['telegram_chat_id']
        self.target_product = self.config['target_product']
        self.target_price = self.config['target_price']
        self.check_interval = self.config.get('check_interval_seconds', 30)
        
        self.stats = {
            'checks_count': 0,
            'alerts_sent': 0,
            'errors': 0,
            'start_time': datetime.now().isoformat()
        }
        
        logging.info("AccBlox Monitor initialized")
        logging.info(f"Target: {self.target_product} @ ${self.target_price}")
        logging.info(f"Check interval: {self.check_interval} seconds")
    
    def scrape_catalog(self):
        """Scrape accblox.net catalog"""
        try:
            url = 'https://accblox.net/'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract products (adjust selectors based on actual website structure)
            products = []
            
            # Look for product cards/items
            product_elements = soup.find_all(['div', 'article'], class_=lambda x: x and any(
                keyword in str(x).lower() for keyword in ['product', 'item', 'card']
            ))
            
            for element in product_elements:
                # Extract product name
                name_elem = element.find(['h1', 'h2', 'h3', 'h4', 'a'], class_=lambda x: x and any(
                    keyword in str(x).lower() for keyword in ['title', 'name', 'product']
                ))
                
                # Extract price
                price_elem = element.find(['span', 'div', 'p'], class_=lambda x: x and 'price' in str(x).lower())
                
                if name_elem and price_elem:
                    name = name_elem.get_text(strip=True)
                    price_text = price_elem.get_text(strip=True)
                    
                    products.append({
                        'name': name,
                        'price': price_text
                    })
            
            # Also search in raw text for the target product
            page_text = soup.get_text()
            if self.target_product.lower() in page_text.lower():
                logging.info(f"Target product name found in page text")
            
            return products
            
        except Exception as e:
            logging.error(f"Error scraping catalog: {e}")
            self.stats['errors'] += 1
            return []
    
    def check_target_product(self, products):
        """Check if target product with target price is found"""
        for product in products:
            name = product['name'].lower()
            price_text = product['price'].lower()
            
            # Check if product name matches
            if self.target_product.lower() in name:
                # Extract numeric price
                import re
                price_match = re.search(r'\$?(\d+\.?\d*)', price_text)
                
                if price_match:
                    price_value = float(price_match.group(1))
                    
                    # Check if price matches target
                    if abs(price_value - self.target_price) < 0.01:
                        logging.info(f"TARGET FOUND: {product['name']} @ {price_text}")
                        return True, product
        
        return False, None
    
    def send_telegram_alert(self, product):
        """Send urgent Telegram alert"""
        try:
            message = f"""URGENT ALERT - TARGET PRODUCT FOUND!

Product: {product['name']}
Price: {product['price']}
Link: https://accblox.net/
Detected: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ACTION REQUIRED - Check website immediately!

Statistics:
- Total checks: {self.stats['checks_count']}
- Alerts sent: {self.stats['alerts_sent'] + 1}
- Running since: {self.stats['start_time']}"""
            
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': message
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            self.stats['alerts_sent'] += 1
            logging.info("Telegram alert sent successfully")
            return True
            
        except Exception as e:
            logging.error(f"Error sending Telegram alert: {e}")
            self.stats['errors'] += 1
            return False
    
    def run(self):
        """Main monitoring loop"""
        logging.info("Starting AccBlox Monitor...")
        
        try:
            while True:
                self.stats['checks_count'] += 1
                
                logging.info(f"Check #{self.stats['checks_count']} - Scraping accblox.net...")
                
                # Scrape catalog
                products = self.scrape_catalog()
                
                if products:
                    logging.info(f"Found {len(products)} products")
                    
                    # Check for target
                    found, product = self.check_target_product(products)
                    
                    if found:
                        self.send_telegram_alert(product)
                    else:
                        logging.info("Target product not found")
                else:
                    logging.warning("No products extracted (may need to adjust scraping logic)")
                
                # Log statistics every 10 checks
                if self.stats['checks_count'] % 10 == 0:
                    logging.info(f"Stats: {self.stats['checks_count']} checks, "
                               f"{self.stats['alerts_sent']} alerts, {self.stats['errors']} errors")
                
                # Wait before next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logging.info("Monitor stopped by user")
        except Exception as e:
            logging.error(f"Fatal error: {e}")
            raise

if __name__ == '__main__':
    monitor = AccBloxMonitor()
    monitor.run()
