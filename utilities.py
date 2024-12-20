import requests
import json
import random
import time
from urllib.parse import quote
from typing import Optional, Dict, List
from loguru import logger


class AutoOrderTest:
    def __init__(self):
        self.session = requests.Session()
        self.guest_id = f"{self.generate_uuid()}"
        self.base_headers = {
            "accept": "application/json",
            "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "cache-control": "no-cache",
            "device-type": "H5",
            "guestid": self.guest_id,
            "pragma": "no-cache",
            "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": "\"Android\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "tenantid": "1",
            "x-requested-with": "XMLHttpRequest"
        }
        self.session.headers.update(self.base_headers)
        self.is_logged_in = False

    def generate_device_id(self) -> str:
        """Generate a random device ID"""
        return ''.join(random.choices('0123456789abcdef', k=32))

    def generate_uuid(self) -> str:
        """Generate a UUID for the request"""
        timestamp = int(time.time() * 1000)
        random_suffix = ''.join(random.choices('0123456789abcdef', k=24))
        return f"{timestamp}_{random_suffix}"

    def login(self, phone: str, password: str) -> bool:
        """Login to the system"""
        try:
            url = "https://m.4008117117.com/api/user/web/login/identify"
            data = {
                "password": password,
                "identify": phone,
                "isApp": True,
                "deviceId": self.generate_device_id(),
                "deviceType": "H5",
                "userAgent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
                "uuid": self.generate_uuid(),
                "deviceSource": "344*882 devices",
            }
            response = self.session.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.is_logged_in = True
                    logger.success(f"Successfully logged in with account {phone}")
                    return True
                else:
                    logger.warning(f"Login failed: {result.get('message')}")
            return False
        except Exception as e:
            logger.exception("Login error")
            return False

    def get_products(self, category_id: str = "8346") -> List[Dict]:
        """Get product list by category"""
        try:
            # 构建基础参数
            params = {
                "pageNo": 1,
                "pageSize": 500,
            }

            if category_id == "3586":  # 积分商城类目
                url = "https://m.4008117117.com/api/item/store/item/searchPointsSkuByCategory"
                params.update({
                    "frontCategoryId": category_id,
                    "storeIds": "1100182001",
                    "promotionRender": "false"
                })
            else:  # 普通商品类目
                url = "https://m.4008117117.com/api/item/store/item/searchStoreSkuByCategory"
                params.update({
                    "frontCategoryId": category_id,
                    "longitude": "120.2126",
                    "latitude": "30.290851",
                    "isFinish": "true"
                })

            # 设置请求头
            headers = {
                **self.base_headers,
                "content-type": "application/json; charset=UTF-8"
            }

            response = requests.get(url, params=params, headers=headers)

            if response.status_code == 200:
                data = response.json()
                logger.debug(f"Response: {json.dumps(data, ensure_ascii=False)}")

                if data.get("success"):
                    # 从 data 中获取所有类目的商品列表
                    all_products = []
                    for category in data.get("data", []):
                        store_sku_list = category.get("storeSkuModelList", [])
                        if store_sku_list:
                            # 添加一个标记，用于区分是否为积分商品
                            for product in store_sku_list:
                                product["is_point_product"] = (category_id == "3586")
                            all_products.extend(store_sku_list)

                    logger.info(f"Found {len(all_products)} products in total")

                    # 记录每个类目的商品数量
                    for category in data.get("data", []):
                        category_name = category.get("categoryName")
                        products_count = len(category.get("storeSkuModelList", []))
                        logger.info(f"Category {category_name}: {products_count} products")

                    return all_products
                else:
                    logger.warning(f"API response not successful: {data.get('message')}")
            else:
                logger.error(f"Request failed with status code: {response.status_code}")
                logger.error(f"Response content: {response.text}")

            return []
        except Exception as e:
            logger.exception(f"Error checking product list: {str(e)}")
            return []

    def get_address_list(self) -> List[Dict]:
        """Get user's address list"""
        try:
            url = "https://m.4008117117.com/api/user/web/shipping-address/self/list-all?app=o2o"
            response = self.session.get(url)

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    addresses = data.get("data", [])
                    logger.info(f"Found {len(addresses)} addresses")
                    return addresses
                else:
                    logger.warning(f"Failed to get addresses: {data.get('message')}")
            return []
        except Exception as e:
            logger.exception("Error getting addresses")
            return []

    def place_order(self, product: Dict, address_id: str) -> bool:
        """Place an order for a product"""
        if not self.is_logged_in:
            logger.error("Not logged in")
            return False

        try:
            # 根据商品类型构建不同的请求数据
            is_point_product = product.get("is_point_product", False)

            # First render the order
            render_url = "https://m.4008117117.com/api/trade/buy/render-order"

            if is_point_product:
                # 构建积分商品的render order请求数据
                render_data = {
                    "deviceSource": "H5",
                    "orderSource": "product.detail.page",
                    "buyConfig": {
                        "lineGrouped": True,
                        "multipleCoupon": True
                    },
                    "orderLineList": [{
                        "skuId": product.get("skuId"),
                        "itemId": product.get("itemId"),
                        "quantity": 1,
                        "promotionTag": None,
                        "activityId": None,
                        "extra": {},
                        "shopId": product.get("storeId", "1100182001")
                    }],
                    "divisionIds": "110000,110100,110105",
                    "addressId": address_id,
                    "couponParams": [{
                        "activityId": None,
                        "benefitId": None,
                        "shopId": 0
                    }],
                    "benefitParams": [],
                    "delivery": {
                        "code": "integralExpress"
                    },
                    "extra": {
                        "activityGroupId": None,
                        "advisorCode": None
                    }
                }

                # 构建referrer URL
                referrer_url = (
                    f"https://m.4008117117.com/intergral/preorder"
                    f"?itemId={product.get('itemId')}"
                    f"&storeId={product.get('storeId', '1100182001')}"
                    f"&type=shop"
                )
            else:
                # 原有的普通商品render order逻辑
                devices_id = self.generate_device_id()
                render_data = {
                    "deviceSource": "H5",
                    "orderSource": "product.detail.page",
                    "buyConfig": {
                        "lineGrouped": True,
                        "multipleCoupon": True
                    },
                    "itemName": product.get("name"),
                    "orderLineList": [{
                        "skuId": product.get("skuId"),
                        "itemId": product.get("itemId"),
                        "quantity": 1,
                        "promotionTag": None,
                        "activityId": None,
                        "extra": {},
                        "shopId": product.get("storeId", "1100078037")
                    }],
                    "divisionIds": "110000,110100,110105",
                    "addressId": address_id,
                    "couponParams": [],
                    "benefitParams": [],
                    "delivery": {
                        "code": "express",
                        "deliveryTimeParam": {}
                    },
                    "extra": {
                        "renewOriginOrderId": "",
                        "renewOriginAddressId": "",
                        "activityGroupId": None,
                        "devicesId": devices_id,
                        "deviceSource": "H5",
                        "channelCode": "SXD",
                        "channelName": "随心订",
                        "operatorType": "1",
                        "paymentMethod": "0",
                        "presentIntegralIsVisible": "1"
                    }
                }

                # URL 编码商品名称和构建 referrer URL
                encoded_item_name = quote(product.get("name", ""))
                referrer_url = (
                    f"https://m.4008117117.com/buyer/preorder"
                    f"?from=itemDetail"
                    f"&itemId={product.get('itemId', '')}"
                    f"&itemName={encoded_item_name}"
                    f"&storeId={product.get('shopId', '1100078037')}"
                    f"&type=shop"
                )

            # 设置请求头
            headers = {
                **self.base_headers,
                "content-type": "application/json; charset=UTF-8",
                "referer": referrer_url
            }

            # 发送render order请求
            render_response = self.session.post(
                render_url,
                json=render_data,
                headers=headers
            )

            if not render_response.ok:
                logger.error(f"Failed to render order: Status code {render_response.status_code}")
                logger.debug(f"Response content: {render_response.text}")
                return False

            render_result = render_response.json()
            if not render_result.get("success"):
                logger.error(f"Failed to render order: {render_result.get('message')}")
                return False

            render_data = render_result.get("data", {})

            if is_point_product:
                # 检查是否可以购买（积分是否足够）
                # purchase_status = render_data.get("purchaseStatus", {})
                # if not purchase_status.get("canBuy", False):
                #     logger.warning(
                #         f"Cannot buy product: {purchase_status.get('content')} ({purchase_status.get('reason')})")
                #     return False

                # 构建积分商品的create order请求数据
                order_data = {
                    "deviceSource": "H5",
                    "orderSource": "product.detail.page",
                    "buyConfig": {
                        "lineGrouped": True,
                        "multipleCoupon": True
                    },
                    "memberPointsDeductionInfo": render_data.get("memberPointsDeductionInfo", {}),
                    "mobile": None,
                    "invoice": None,
                    "addressId": address_id,
                    "couponParams": [{
                        "activityId": -1,
                        "benefitId": None,
                        "shopId": 0
                    }, {
                        "activityId": -1,
                        "benefitId": None,
                        "shopId": product.get("storeId", "1100182001")
                    }],
                    "benefitParams": [{
                        "activityId": -1,
                        "benefitId": None,
                        "shopId": 0,
                        "benefitType": None,
                        "amount": None
                    }],
                    "orderList": render_data.get("orderList", []),
                    "extraParam": {"cartLineIds": None},
                    "extra": {
                        "advisorCode": None,
                        "orderSource": "product.detail.page",
                        "settleAccountName": None,
                        "deviceSource": "H5",
                        "paymentMethod": "0",
                        "channelName": "随心订",
                        "operatorType": "1",
                        "settleAccountId": "null",
                        "advisorText": "光明健康顾问编号为7-8位数\\n光明健康顾问编号由字母及数字组成\\n光明健康顾问编号内字母为大写字母",
                        "activityGroupId": None,
                        "channelCode": "SXD",
                        "presentIntegralIsVisible": "1"
                    },
                    "delivery": {
                        "code": "integralExpress",
                        "deliveryTimeParam": {}
                    }
                }

                headers["referer"] = "https://m.4008117117.com/intergral/cashier"
            else:
                # 原有的普通商品下单逻辑...
                order_data = {
                    # 原有的普通商品order_data内容
                    "deviceSource": "H5",
                    "orderSource": "product.detail.page",
                    "buyConfig": {
                        "lineGrouped": True,
                        "multipleCoupon": True
                    },
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
                        "presentIntegral": render_data['memberPointsDeductionInfo']['presentIntegral']
                    },
                    "itemName": product.get("name"),
                    "mobile": None,
                    "invoice": None,
                    "addressId": address_id,
                    "couponParams": [{
                        "activityId": -1,
                        "benefitId": None,
                        "shopId": 0
                    }, {
                        "activityId": -1,
                        "benefitId": None,
                        "shopId": product.get("storeId", "1100078037")
                    }],
                    "benefitParams": [{
                        "activityId": -1,
                        "benefitId": None,
                        "shopId": 0,
                        "benefitType": None,
                        "amount": None
                    }],
                    "orderList": render_data.get("orderList", []),
                    "delivery": {
                        "code": "express",
                        "deliveryTimeParam": {}
                    },
                    "extra": {
                        "orderSource": "product.detail.page",
                        "settleAccountName": "上海光明随心订电子商务有限公司",
                        "settleAccountId": "52",
                        "advisorText": "光明健康顾问编号为7-8位数\\n光明健康顾问编号由字母及数字组成\\n光明健康顾问编号内字母为大写字母",
                        "renewOriginAddressId": "",
                        "devicesId": devices_id,
                        "deviceSource": "H5",
                        "renewOriginOrderId": "",
                        "paymentMethod": "0",
                        "channelName": "随心订",
                        "customerId": None,
                        "customerName": None,
                        "operatorType": "1",
                        "activityGroupId": None,
                        "channelCode": "SXD",
                        "presentIntegralIsVisible": "1",
                        "needUpstairs": "0",
                        "needMilkBox": "0",
                        "isFreeOrder": 0
                    },
                    "extraParam": {"cartLineIds": None}
                }

            # 创建订单
            create_url = "https://m.4008117117.com/api/trade/buy/create-order"
            order_response = self.session.post(
                create_url,
                json=order_data,
                headers=headers
            )

            if order_response.status_code == 200:
                result = order_response.json()
                if result.get("success"):
                    order_info = result.get("data", {})
                    logger.success(f"Successfully placed order for {product.get('name')}")
                    logger.info(f"Purchase order ID: {order_info.get('purchaseOrderId')}")
                    logger.info(f"Order details: {json.dumps(order_info, ensure_ascii=False)}")
                    return True
                else:
                    logger.warning(f"Failed to create order: {result.get('message')}")
                    logger.debug(f"Full response: {json.dumps(result, ensure_ascii=False)}")
            else:
                logger.error(f"Order creation failed with status code: {order_response.status_code}")
                logger.debug(f"Response content: {order_response.text}")

            return False

        except Exception as e:
            logger.exception("Error placing order")
            return False


if __name__ == "__main__":
    # 配置logger
    logger.remove()
    logger.add(
        "test_logs.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        level="DEBUG",
    )
    logger.add(
        lambda msg: print(msg),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        level="INFO",
        colorize=True
    )

    # 测试账号信息
    TEST_PHONE = "16778641768"
    TEST_PASSWORD = "gp414231"

    try:
        # 创建测试实例
        auto_order = AutoOrderTest()

        # 测试登录
        logger.info("Testing login...")
        if auto_order.login(TEST_PHONE, TEST_PASSWORD):
            logger.success("Login successful")

            while 1:
                # 测试获取商品列表
                logger.info("Testing get products...")
                products = auto_order.get_products('3586')
                # products = auto_order.get_products('8338')
                # products = auto_order.get_products()
                if products:
                    logger.success(f"Successfully retrieved {len(products)} products")

                    # 测试获取地址列表
                    logger.info("Testing get addresses...")
                    addresses = auto_order.get_address_list()
                    if addresses:
                        logger.success(f"Successfully retrieved {len(addresses)} addresses")

                        # 测试下单（仅在有地址和商品的情况下）
                        if products and addresses:
                            logger.info("Testing place order...")
                            test_product = products[-1]  # 使用第一个商品测试
                            test_address = addresses[0]  # 使用第一个地址测试
                            if auto_order.place_order(test_product, test_address.get("id")):
                                logger.success("Order placed successfully")
                            else:
                                logger.error("Failed to place order")
                    else:
                        logger.error("No addresses found")
                else:
                    logger.error("No products found")
        else:
            logger.error("Login failed")

    except Exception as e:
        logger.exception("Test failed with error")
