from loguru import logger
import sys
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import os
import random
from queue import Queue
from threading import Lock
import requests
import json


# 配置 loguru
def setup_logger():
    """配置 loguru logger"""
    # 移除默认的 sink
    logger.remove()

    # 添加控制台输出
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True
    )

    # 添加文件输出
    logger.add(
        "logs/auto_order_{time}.log",  # 每次运行创建新的日志文件
        rotation="500 MB",  # 文件大小超过500MB后轮换
        retention="10 days",  # 保留10天的日志
        compression="zip",  # 压缩旧日志
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        encoding="utf-8"
    )

    # 添加错误专用日志文件
    logger.add(
        "logs/errors_{time}.log",
        rotation="100 MB",
        retention="30 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        encoding="utf-8",
        backtrace=True,  # 启用详细的异常回溯
        diagnose=True  # 启用诊断信息
    )


@dataclass
class Account:
    phone: str
    password: str
    session: Optional[requests.Session] = None
    proxy: Optional['Proxy'] = None
    is_logged_in: bool = False
    last_login_time: Optional[datetime] = None
    login_failures: int = 0

    def __str__(self):
        return f"Account(phone={self.phone}, proxy={self.proxy.host if self.proxy else None})"


@dataclass
class Proxy:
    host: str
    port: str
    username: str = None
    password: str = None
    in_use: bool = False

    def __str__(self):
        return f"{self.host}:{self.port}"


@dataclass
class ProductCriteria:
    category_id: str = "8329"
    max_price: float = None
    keywords: List[str] = None


class AccountManager:
    def __init__(self):
        self.accounts: Dict[str, Account] = {}
        self.available_accounts = Queue()
        self.lock = Lock()

    def add_account(self, account: Account):
        with self.lock:
            self.accounts[account.phone] = account
            self.available_accounts.put(account.phone)
            logger.info(f"Added account {account.phone} to pool")

    def get_next_available_account(self) -> Optional[Account]:
        try:
            phone = self.available_accounts.get_nowait()
            account = self.accounts[phone]
            logger.debug(f"Got account {account} from pool")
            return account
        except:
            logger.debug("No available accounts in pool")
            return None

    def return_account(self, account: Account):
        with self.lock:
            self.available_accounts.put(account.phone)
            logger.debug(f"Returned account {account} to pool")


class ProxyManager:
    def __init__(self):
        self.proxies: List[Proxy] = []
        self.lock = Lock()

    def add_proxy(self, proxy: Proxy):
        with self.lock:
            self.proxies.append(proxy)
            logger.debug(f"Added proxy {proxy} to pool")

    def get_available_proxy(self) -> Optional[Proxy]:
        with self.lock:
            available = [p for p in self.proxies if not p.in_use]
            if available:
                proxy = random.choice(available)
                proxy.in_use = True
                logger.debug(f"Assigned proxy {proxy}")
                return proxy
            logger.warning("No available proxies")
            return None

    def release_proxy(self, proxy: Proxy):
        with self.lock:
            proxy.in_use = False
            logger.debug(f"Released proxy {proxy}")


class AutoOrderService:
    def __init__(self, accounts_file: str, proxies_file: str, check_interval: int = 1):
        # 确保日志目录存在
        os.makedirs("logs", exist_ok=True)

        # 设置日志
        setup_logger()
        logger.info("Initializing AutoOrderService")

        self.account_manager = AccountManager()
        self.proxy_manager = ProxyManager()
        self.check_interval = check_interval

        # Load accounts and proxies
        self.load_accounts(accounts_file)
        self.load_proxies(proxies_file)

        self.base_headers = {
            "accept": "application/json",
            "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "device-type": "H5",
            "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": "\"Android\"",
            "tenantid": "1",
        }

        # Initialize account sessions with proxies
        self.initialize_account_sessions()

    def load_accounts(self, filename: str):
        """Load accounts from text file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        phone, password = line.strip().split(',')
                        account = Account(phone=phone, password=password)
                        self.account_manager.add_account(account)
            logger.info(f"Successfully loaded {len(self.account_manager.accounts)} accounts")
        except Exception as e:
            logger.exception(f"Failed to load accounts from {filename}")
            raise

    def load_proxies(self, filename: str):
        """Load proxies from text file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        parts = line.strip().split(':')
                        if len(parts) >= 2:
                            proxy = Proxy(host=parts[0], port=parts[1])
                            if len(parts) >= 4:
                                proxy.username = parts[2]
                                proxy.password = parts[3]
                            self.proxy_manager.add_proxy(proxy)
            logger.info(f"Successfully loaded {len(self.proxy_manager.proxies)} proxies")
        except Exception as e:
            logger.exception(f"Failed to load proxies from {filename}")
            raise

    def initialize_account_sessions(self):
        """Initialize sessions for all accounts and assign proxies"""
        logger.info("Initializing account sessions and assigning proxies")
        for account in self.account_manager.accounts.values():
            try:
                # Create new session
                account.session = requests.Session()
                account.session.headers.update(self.base_headers)

                # Assign proxy
                proxy = self.proxy_manager.get_available_proxy()
                if proxy:
                    account.proxy = proxy
                    proxy_url = f"http://{proxy.host}:{proxy.port}"
                    if proxy.username and proxy.password:
                        proxy_url = f"http://{proxy.username}:{proxy.password}@{proxy.host}:{proxy.port}"
                    account.session.proxies = {
                        'http': proxy_url,
                        'https': proxy_url
                    }
                    logger.info(f"Successfully initialized session for account {account}")
                else:
                    logger.warning(f"No proxy available for account {account.phone}")
            except Exception as e:
                logger.exception(f"Failed to initialize session for account {account.phone}")

    def generate_device_id(self) -> str:
        """Generate a random device ID"""
        return ''.join(random.choices('0123456789abcdef', k=32))

    def generate_uuid(self) -> str:
        """Generate a UUID for the request"""
        timestamp = int(time.time() * 1000)
        random_suffix = ''.join(random.choices('0123456789abcdef', k=24))
        return f"{timestamp}_{random_suffix}"

    @logger.catch
    def login_account(self, account: Account) -> bool:
        """Login with specific account"""
        if account.is_logged_in:
            logger.debug(f"Account {account.phone} already logged in")
            return True

        logger.info(f"Attempting to login account {account.phone}")
        try:
            url = "https://m.4008117117.com/api/user/web/login/identify"

            data = {
                "password": account.password,
                "identify": account.phone,
                "isApp": True,
                "deviceId": self.generate_device_id(),
                "deviceType": "H5",
                "userAgent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
                "uuid": self.generate_uuid(),
                "deviceSource": "344*882 devices",
            }

            response = account.session.post(url, json=data)

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    account.is_logged_in = True
                    account.last_login_time = datetime.now()
                    account.login_failures = 0
                    logger.success(f"Successfully logged in with account {account.phone}")
                    return True
                else:
                    account.login_failures += 1
                    logger.warning(f"Login failed for account {account.phone}: {result.get('message')}")
            return False
        except Exception as e:
            account.login_failures += 1
            logger.exception(f"Login error for account {account.phone}")
            return False

    @logger.catch
    def check_product_list(self, account: Account, criteria: ProductCriteria) -> List[Dict]:
        """Check product list using specific account"""
        try:
            url = "https://m.4008117117.com/api/item/store/item/searchStoreSkuByCategory"
            params = {
                "pageNo": 1,
                "pageSize": 500,
                "frontCategoryId": criteria.category_id,
                "longitude": "120.2126",
                "latitude": "30.290851",
                "isFinish": "true"
            }

            logger.debug(f"Checking products with account {account.phone}")
            response = account.session.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    products = data.get("data", {}).get("records", [])
                    matching_products = self.filter_products(products, criteria)
                    logger.info(f"Found {len(matching_products)} matching products")
                    return matching_products
                else:
                    logger.warning(f"Failed to get product list: {data.get('message')}")
            else:
                logger.error(f"Failed to get product list, status code: {response.status_code}")

            return []
        except Exception as e:
            logger.exception(f"Error checking product list with account {account.phone}")
            return []

    def filter_products(self, products: List[Dict], criteria: ProductCriteria) -> List[Dict]:
        """Filter products based on criteria"""
        matching_products = []

        for product in products:
            try:
                if criteria.max_price and product.get("salePrice", 0) > criteria.max_price:
                    continue

                if criteria.keywords:
                    name = product.get("name", "").lower()
                    if not any(keyword.lower() in name for keyword in criteria.keywords):
                        continue

                matching_products.append(product)
                logger.debug(f"Found matching product: {product.get('name')}")
            except Exception as e:
                logger.exception(f"Error filtering product: {product}")

        return matching_products

    @logger.catch
    def place_order(self, account: Account, product: Dict) -> bool:
        """Place order using specific account"""
        if not account.is_logged_in:
            if not self.login_account(account):
                return False

        try:
            # 1. First render the order
            render_response = self.render_order(account, product)
            if not render_response:
                return False

            # 2. Create the actual order
            order_response = self.create_order(account, product, render_response)
            if order_response:
                logger.success(f"Successfully placed order for {product.get('name')} with account {account.phone}")
                return True
            else:
                logger.error(f"Failed to create order for {product.get('name')} with account {account.phone}")
                return False
        except Exception as e:
            logger.exception(f"Error placing order with account {account.phone}")
            return False

    @logger.catch
    def render_order(self, account: Account, product: Dict) -> Optional[Dict]:
        """Render order before placing it"""
        try:
            url = "https://m.4008117117.com/api/trade/buy/render-order"

            data = {
                "deviceSource": "H5",
                "orderSource": "product.detail.page",
                "buyConfig": {"lineGrouped": True, "multipleCoupon": True},
                "itemName": product.get("name"),
                "orderLineList": [{
                    "skuId": product.get("skuId"),
                    "itemId": product.get("itemId"),
                    "quantity": 1,
                    "promotionTag": None,
                    "activityId": None,
                    "extra": {},
                    "shopId": product.get("shopId")
                }],
                "divisionIds": "110000,110100,110105",
                "addressId": None,
                "couponParams": [],
                "benefitParams": [],
                "delivery": {},
                "extra": {
                    "renewOriginOrderId": "",
                    "renewOriginAddressId": "",
                    "activityGroupId": None
                },
                "devicesId": self.generate_device_id(),
            }

            response = account.session.post(url, json=data)

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.debug(f"Successfully rendered order for {product.get('name')}")
                    return result.get("data")
                else:
                    logger.warning(f"Failed to render order: {result.get('message')}")
            else:
                logger.error(f"Failed to render order, status code: {response.status_code}")

            return None
        except Exception as e:
            logger.exception("Error rendering order")
            return None

    @logger.catch
    def create_order(self, account: Account, product: Dict, render_data: Dict) -> bool:
        """Create the actual order"""
        try:
            url = "https://m.4008117117.com/api/trade/buy/create-order"

            data = {
                "deviceSource": "H5",
                "orderSource": "product.detail.page",
                "buyConfig": {"lineGrouped": True, "multipleCoupon": True},
                "memberPointsDeductionInfo": {
                    "available": False,
                    "visible": False,
                    "point": 0,
                    "chosenIntegral": 0,
                    "maxExchangeValue": 0,
                    "minExchangeValue": 100,
                    "exchangeUnit": 100,
                    "deductAmount": 0,
                    "exchangeRatio": 1,
                    "displayRemark": None,
                    "extra": None,
                    "presentIntegral": render_data.get("memberPointsDeductionInfo", {}).get("presentIntegral", 0)
                },
                "itemName": product.get("name"),
                "mobile": None,
                "invoice": None,
                "addressId": render_data.get("addressId"),
                "couponParams": [
                    {"activityId": -1, "benefitId": None, "shopId": 0},
                    {"activityId": -1, "benefitId": None, "shopId": product.get("shopId")}
                ],
                "benefitParams": [
                    {
                        "activityId": -1,
                        "benefitId": None,
                        "shopId": 0,
                        "benefitType": None,
                        "amount": None
                    }
                ],
                "orderList": [{
                    "activityOrderList": [{
                        "activityMatchedLine": {
                            "activity": None,
                            "valid": False,
                            "benefitId": None,
                            "benefitUsageInfo": None,
                            "display": None,
                            "matchedLineIds": None,
                            "errorMsg": None
                        },
                        "activityExist": False,
                        "orderLineList": None,
                        "orderLineGroups": [{
                            "orderLineList": [{
                                "itemId": product.get("itemId"),
                                "skuId": product.get("skuId"),
                                "skuCode": product.get("skuCode"),
                                "bundleId": None,
                                "quantity": 1,
                                "activityId": None,
                                "shopActivityId": None,
                                "extraParam": None,
                                "promotionTag": None,
                                "shopId": product.get("shopId"),
                                "lineId": f"{product.get('skuId')}_{product.get('shopId')}",
                                "categoryId": product.get("categoryId"),
                                "skuName": product.get("name"),
                                "attrs": product.get("attrs", []),
                                "mainImage": product.get("mainImage"),
                                "outerSkuCode": None,
                                "status": 1,
                                "salePrice": product.get("salePrice"),
                                "preferSalePrice": product.get("preferSalePrice", product.get("salePrice")),
                                "extra": render_data.get("orderLineList", [{}])[0].get("extra", {}),
                                "summary": {
                                    "deposit": None,
                                    "balanceDue": None,
                                    "taxFee": 0,
                                    "summary": product.get("salePrice"),
                                    "skuFee": product.get("salePrice")
                                },
                                "bizCode": "express",
                                "itemAttributes": render_data.get("orderLineList", [{}])[0].get("itemAttributes", {})
                            }]
                        }]
                    }],
                    "shop": render_data.get("orderList", [{}])[0].get("shop", {}),
                    "buyerNote": None,
                    "extraParam": None,
                    "priceInfo": {
                        "allDiscount": 0,
                        "couponTotal": 0,
                        "shopDiscountFee": 0,
                        "platformDiscountFee": 0,
                        "benefitDiscountFee": 0,
                        "totalTaxFee": 0,
                        "skuTotalFee": product.get("salePrice"),
                        "skuOriginTotalFee": product.get("salePrice"),
                        "shipFeeTotal": 0,
                        "inviterTotalFee": 0,
                        "memberPointDeductTotal": 0,
                        "sellCouponTotalFee": 0,
                        "nonCouponTotal": 0,
                        "totalFee": product.get("salePrice")
                    },
                    "shipFeeInfo": render_data.get("orderList", [{}])[0].get("shipFeeInfo", {})
                }],
                "extraParam": {"cartLineIds": None},
                "extra": {
                    "orderSource": "product.detail.page",
                    "settleAccountName": render_data.get("extra", {}).get("settleAccountName"),
                    "settleAccountId": render_data.get("extra", {}).get("settleAccountId"),
                    "advisorText": render_data.get("extra", {}).get("advisorText"),
                    "customerName": None,
                    "renewOriginAddressId": "",
                    "devicesId": self.generate_device_id(),
                    "deviceSource": "H5",
                    "customerId": None,
                    "renewOriginOrderId": "",
                    "paymentMethod": "0",
                    "channelName": "随心订",
                    "operatorType": "1",
                    "activityGroupId": None,
                    "channelCode": "SXD",
                    "presentIntegralIsVisible": "1"
                },
                "delivery": {
                    "code": "express",
                    "deliveryTimeParam": {}
                }
            }

            response = account.session.post(url, json=data)

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.success(f"Successfully created order for {product.get('name')}")
                    return True
                else:
                    logger.warning(f"Failed to create order: {result.get('message')}")
            else:
                logger.error(f"Failed to create order, status code: {response.status_code}")

            return False
        except Exception as e:
            logger.exception("Error creating order")
            return False

    def run(self, criteria: ProductCriteria):
        """Main service loop"""
        logger.info("Starting auto order service")

        # First login all accounts
        logger.info("Performing initial login for all accounts")
        for account in self.account_manager.accounts.values():
            self.login_account(account)

        logger.info("Entering main monitoring loop")
        while True:
            try:
                # Get next available account
                account = self.account_manager.get_next_available_account()
                if not account:
                    logger.debug("No available accounts, waiting...")
                    time.sleep(1)
                    continue

                # Check products with this account
                matching_products = self.check_product_list(account, criteria)

                if matching_products:
                    logger.info(f"Found {len(matching_products)} matching products")
                    # Try to place orders
                    for product in matching_products:
                        if self.place_order(account, product):
                            logger.success(
                                f"Successfully ordered product: {product.get('name')} with account {account.phone}")
                        else:
                            logger.error(f"Failed to order product: {product.get('name')} with account {account.phone}")
                else:
                    logger.debug(f"No matching products found for current criteria")

                # Return account to pool
                self.account_manager.return_account(account)

                # Wait before next check
                logger.debug(f"Waiting {self.check_interval} seconds before next check")
                time.sleep(self.check_interval)

            except Exception as e:
                logger.exception("Error in main service loop")
                if account:
                    self.account_manager.return_account(account)
                time.sleep(self.check_interval)


if __name__ == "__main__":
    try:
        # Configuration
        ACCOUNTS_FILE = "accounts.txt"
        PROXIES_FILE = "proxies.txt"
        CHECK_INTERVAL = 30  # seconds

        # Create criteria for products
        criteria = ProductCriteria(
            category_id="8329",
            max_price=5000,
            keywords=["星座挂件"]
        )

        # Start service
        logger.info("Starting application")
        service = AutoOrderService(ACCOUNTS_FILE, PROXIES_FILE, CHECK_INTERVAL)
        service.run(criteria)
    except KeyboardInterrupt:
        logger.warning("Service stopped by user")
    except Exception as e:
        logger.exception("Service crashed")
        raise
