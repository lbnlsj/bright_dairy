import threading
import random
import queue
import time
from pathlib import Path
from typing import List, Dict, Optional, Set
from datetime import datetime
from loguru import logger
import traceback

from utilities import AutoOrderTest


class ProxyManager:
    def __init__(self, proxy_file: str = "data/proxies.txt"):
        self.proxy_file = proxy_file
        self.proxies = self._load_proxies()
        self._lock = threading.Lock()

    def _load_proxies(self) -> List[str]:
        """Load proxies from file"""
        try:
            proxy_path = Path(self.proxy_file)
            if proxy_path.exists():
                with open(proxy_path, 'r', encoding='utf-8') as f:
                    return [line.strip() for line in f if line.strip()]
            return []
        except Exception as e:
            logger.error(f"Failed to load proxies: {e}")
            return []

    def get_random_proxy(self) -> Optional[str]:
        """Get a random proxy from the pool"""
        with self._lock:
            return random.choice(self.proxies) if self.proxies else None


class AccountManager:
    def __init__(self, accounts: List[Dict]):
        self.accounts = accounts
        self.auto_orders: Dict[str, AutoOrderTest] = {}
        self._lock = threading.Lock()

    def initialize_all_accounts(self) -> None:
        """Initialize all accounts with login"""
        for account in self.accounts:
            phone = account['phone']
            auto_order = AutoOrderTest()
            if auto_order.login(phone, account['password']):
                logger.success(f"Account {phone} initialized and logged in successfully")
                self.auto_orders[phone] = auto_order
            else:
                logger.error(f"Failed to initialize account {phone}")

    def get_auto_order(self, phone: str) -> Optional[AutoOrderTest]:
        """Get AutoOrderTest instance for account"""
        return self.auto_orders.get(phone)


class OrderTracker:
    def __init__(self):
        self.ordered_items: Dict[str, Set[str]] = {}  # account -> set of ordered item IDs
        self._lock = threading.Lock()

    def is_ordered(self, account_phone: str, item_id: str) -> bool:
        """Check if item was already ordered by account"""
        with self._lock:
            return item_id in self.ordered_items.get(account_phone, set())

    def mark_ordered(self, account_phone: str, item_id: str) -> None:
        """Mark item as ordered by account"""
        with self._lock:
            if account_phone not in self.ordered_items:
                self.ordered_items[account_phone] = set()
            self.ordered_items[account_phone].add(item_id)


class MonitorTask:
    def __init__(self, accounts: List[Dict], categories: List[Dict],
                 activity_log_queue: queue.Queue, point_log_queue: queue.Queue):
        self.account_manager = AccountManager(accounts)
        self.categories = categories
        self.proxy_manager = ProxyManager()
        self.order_tracker = OrderTracker()
        self.activity_log_queue = activity_log_queue
        self.point_log_queue = point_log_queue
        self.is_running = False
        self.threads: List[threading.Thread] = []
        self._lock = threading.Lock()

    def log_activity(self, message: str) -> None:
        """Log activity message to frontend"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.activity_log_queue.put(f"[{timestamp}] {message}")
        logger.info(message)

    def log_point(self, message: str) -> None:
        """Log point-related message to frontend"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.point_log_queue.put(f"[{timestamp}] {message}")
        logger.info(message)

    def _monitor_category(self, category: Dict):
        """Monitor single category"""
        while self.is_running:
            try:
                # Create temporary instance for product checking
                checker = AutoOrderTest()

                # Get products for this category
                products = checker.get_products(category['area_id'])
                if not products:
                    self.log_activity(f"No products found in category {category['name']}")
                    time.sleep(random.uniform(2, 4))
                    continue

                # Check each product
                for product in products:
                    if not self.is_running:
                        break

                    if product['name'].lower().find(category['name'].lower()) == -1:
                        continue

                    # Try with each logged-in account
                    for account in self.account_manager.accounts:
                        phone = account['phone']

                        # Skip if already ordered
                        if self.order_tracker.is_ordered(phone, product['itemId']):
                            continue

                        auto_order = self.account_manager.get_auto_order(phone)
                        if not auto_order:
                            continue

                        # Get address list
                        addresses = auto_order.get_address_list()
                        if not addresses:
                            continue

                        # Attempt to place order
                        if auto_order.place_order(product, addresses[0]['id']):
                            self.order_tracker.mark_ordered(phone, product['itemId'])
                            if product.get('is_point_product'):
                                self.log_point(
                                    f"Successfully ordered point product {product['name']} "
                                    f"with account {phone}"
                                )
                            else:
                                self.log_activity(
                                    f"Successfully ordered activity product {product['name']} "
                                    f"with account {phone}"
                                )

                        time.sleep(random.uniform(0.5, 1.5))

            except Exception as e:
                logger.exception(f"Error monitoring category {category['name']}: {str(e)}")
                if category['area_id'] == "3586":
                    self.log_point(f"Error in point category {category['name']}: {str(e)}")
                else:
                    self.log_activity(f"Error in activity category {category['name']}: {str(e)}")
                traceback.print_exc()

            time.sleep(random.uniform(2, 4))

    def start(self):
        """Start monitoring"""
        with self._lock:
            if self.is_running:
                return

            self.is_running = True

            # Initialize all accounts first
            self.log_activity("Initializing accounts...")
            self.account_manager.initialize_all_accounts()

            # Create monitoring thread for each category
            for category in self.categories:
                thread = threading.Thread(
                    target=self._monitor_category,
                    args=(category,),
                    daemon=True
                )
                thread.start()
                self.threads.append(thread)

                if category['area_id'] == "3586":
                    self.log_point(f"Started monitoring point category: {category['name']}")
                else:
                    self.log_activity(f"Started monitoring activity category: {category['name']}")

            logger.info(f"Monitor started with {len(self.categories)} categories")

    def stop(self):
        """Stop monitoring"""
        with self._lock:
            if not self.is_running:
                return

            self.is_running = False

            # Wait for all threads to finish
            for thread in self.threads:
                thread.join(timeout=5.0)

            self.threads.clear()
            self.log_activity("Monitor stopped")