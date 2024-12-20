import requests

session = requests.session()

def treefrontC():

    url = "https://m.4008117117.com/api/item/shop-category/tree?frontCategoryId=4403&longitude=120.2126&latitude=30.290851&isFinish=true"

    headers = {
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "cache-control": "no-cache",
        "device-type": "H5",
        "guestid": "090e4de0-20bb-4d59-8f6e-af7076f2aea4",
        "pragma": "no-cache",
        "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "\"Android\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "tenantid": "1",
        "x-requested-with": "XMLHttpRequest",
    }

    response = session.get(url, headers=headers)

    print(response.status_code)

    return response.text

##################################################

def searchStor():

    url = "https://m.4008117117.com/api/item/store/item/searchStoreSkuByCategory?pageNo=1&pageSize=500&frontCategoryId=8329&longitude=120.2126&latitude=30.290851&isFinish=true"

    headers = {
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "cache-control": "no-cache",
        "device-type": "H5",
        "guestid": "090e4de0-20bb-4d59-8f6e-af7076f2aea4",
        "pragma": "no-cache",
        "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "\"Android\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "tenantid": "1",
        "x-requested-with": "XMLHttpRequest",
    }

    response = session.get(url, headers=headers)

    print(response.status_code)

    return response.text

##################################################

def identify():

    url = "https://m.4008117117.com/api/user/web/login/identify"

    headers = {
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "cache-control": "no-cache",
        "content-type": "application/json; charset=UTF-8",
        "device-type": "H5",
        "guestid": "621edd0b-931a-48aa-9d24-018599992f5f",
        "pragma": "no-cache",
        "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "\"Android\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "tenantid": "1",
        "x-requested-with": "XMLHttpRequest",
    }

    data = {
        "password": 'gbaycm123',
        "identify": '15557581380',
        "isApp": True,
        "deviceId": '68e07a174825b8bc0ee0769ef6ee03fc',
        "deviceType": 'H5',
        "userAgent": 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36',
        "uuid": '1733798081506_65b8e9f97052cc46a498',
        "deviceSource": '344*882 devices',
    }

    response = session.post(url, headers=headers, json=data)

    print(response.status_code)

    return response.text

##################################################

def render_ord():

    url = "https://m.4008117117.com/api/trade/buy/render-order"

    headers = {
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "cache-control": "no-cache",
        "content-type": "application/json; charset=UTF-8",
        "device-type": "H5",
        "guestid": "621edd0b-931a-48aa-9d24-018599992f5f",
        "pragma": "no-cache",
        "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "\"Android\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "tenantid": "1",
        "x-requested-with": "XMLHttpRequest",
    }

    data = {
        "deviceSource": 'H5',
        "orderSource": 'product.detail.page',
        "buyConfig": {'lineGrouped': True, 'multipleCoupon': True},
        "itemName": '随小订星座挂件--双子座',
        "orderLineList": [{'skuId': 110005200318001, 'itemId': 110005200318001, 'quantity': 1, 'promotionTag': None, 'activityId': None, 'extra': {}, 'shopId': 1100078037}],
        "divisionIds": '110000,110100,110105',
        "addressId": None,
        "couponParams": [],
        "benefitParams": [],
        "delivery": {},
        "extra": {'renewOriginOrderId': '', 'renewOriginAddressId': '', 'activityGroupId': None},
        "devicesId": 'f7dd9fc1ac130149157842fb56a508ad',
    }

    response = session.post(url, headers=headers, json=data)

    print(response.status_code)

    return response.text

##################################################

def create_ord():

    url = "https://m.4008117117.com/api/trade/buy/create-order"

    headers = {
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "cache-control": "no-cache",
        "content-type": "application/json; charset=UTF-8",
        "device-type": "H5",
        "guestid": "621edd0b-931a-48aa-9d24-018599992f5f",
        "pragma": "no-cache",
        "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "\"Android\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "tenantid": "1",
        "x-requested-with": "XMLHttpRequest",
    }

    data = {
        "deviceSource": 'H5',
        "orderSource": 'product.detail.page',
        "buyConfig": {'lineGrouped': True, 'multipleCoupon': True},
        "memberPointsDeductionInfo": {'available': False, 'visible': False, 'point': 0, 'chosenIntegral': 0, 'maxExchangeValue': 0, 'minExchangeValue': 100, 'exchangeUnit': 100, 'deductAmount': 0, 'exchangeRatio': 1, 'displayRemark': None, 'extra': None, 'presentIntegral': 29},
        "itemName": '随小订星座挂件--双子座',
        "mobile": None,
        "invoice": None,
        "addressId": 32189953,
        "couponParams": [{'activityId': -1, 'benefitId': None, 'shopId': 0}, {'activityId': -1, 'benefitId': None, 'shopId': 1100078037}],
        "benefitParams": [{'activityId': -1, 'benefitId': None, 'shopId': 0, 'benefitType': None, 'amount': None}],
        "orderList": [{'activityOrderList': [{'activityMatchedLine': {'activity': None, 'valid': False, 'benefitId': None, 'benefitUsageInfo': None, 'display': None, 'matchedLineIds': None, 'errorMsg': None}, 'activityExist': False, 'orderLineList': None, 'orderLineGroups': [{'orderLineList': [{'itemId': 110005200318001, 'skuId': 110005200318001, 'skuCode': 'goods1134', 'bundleId': None, 'quantity': 1, 'activityId': None, 'shopActivityId': None, 'extraParam': None, 'promotionTag': None, 'shopId': 1100078037, 'lineId': '110005200318001_1100078037', 'categoryId': 1514, 'skuName': '随小订星座挂件--双子座', 'attrs': [{'attrVal': '63g*1', 'attrKey': '规格'}], 'mainImage': 'https://assets.4008117117.com/upload/2021/6/28/7e3c2f33-1bc0-4864-b54d-e036684522e4.jpg', 'outerSkuCode': None, 'status': 1, 'salePrice': 2900, 'preferSalePrice': 2900, 'extra': {'devicesId': 'f7dd9fc1ac130149157842fb56a508ad', 'fullUnit': '63g*1', 'itemType': '1', 'shopType': None, 'deliveryTimeType': None, 'businessCode': 'express', 'businessName': '快递', 'businessType': '1', 'unitQuantity': '1', 'categoryList': '[1514,1508]'}, 'summary': {'deposit': None, 'balanceDue': None, 'taxFee': 0, 'summary': 2900, 'skuFee': 2900}, 'bizCode': 'express', 'itemAttributes': {'saleUnitName': None, 'grossWeight': '63', 'fullUnit': '63g*1', 'innerProduct': 'true', 'erpCode': '11190105', 'categoryList': '[1514,1508]', 'weight': '63', 'frontCategoryIdList': '[4161,4162,4835,4100,4836,4101,4837,5029,5030,5031,3571,3572,8212,3573,3574,8346,8348]', 'skuCode': 'goods1134', 'updatedAt': '1719759871000'}}]}]}], 'shop': {'tenantId': None, 'tenantIdLong': None, 'extra': {'shipper': 'null', 'clearable': '0', 'erpAccountCode': '1201', 'priceTemplateId': '1000000000330', 'sellerName': '上海光明随心订电子商务有限公司', 'supportDelivery': '1', 'defaultDeliveryTemplateId': '91', 'organizationId': '20406', 'supportPickUp': '0', 'sellerId': '52', 'shopType': '4', 'settlementSubjectId': '52', 'updatedAt': '1728890571000'}, 'id': 1100078037, 'outerId': '1100078037', 'userId': 52, 'userName': None, 'name': '光明随心订自营快递', 'status': 1, 'type': 1, 'phone': None, 'businessId': 52, 'imageUrl': None, 'address': None, 'email': None, 'tags': None, 'buyerNote': None, 'businessType': 7201}, 'buyerNote': None, 'extraParam': None, 'priceInfo': {'allDiscount': 0, 'couponTotal': 0, 'shopDiscountFee': 0, 'platformDiscountFee': 0, 'benefitDiscountFee': 0, 'totalTaxFee': 0, 'skuTotalFee': 2900, 'skuOriginTotalFee': 2900, 'shipFeeTotal': 0, 'inviterTotalFee': 0, 'memberPointDeductTotal': 0, 'sellCouponTotalFee': 0, 'nonCouponTotal': 0, 'totalFee': 2900}, 'shipFeeInfo': {'visible': False, 'shipFeeDiscount': 0, 'shipFeeTotal': 0, 'shipFeeOriginTotal': 0, 'shipFeeDetailList': [{'shipFeeTemplateList': [{'shipFeeLineList': [{'lineId': '110005200318001_1100078037', 'skuImg': 'https://assets.4008117117.com/upload/2021/6/28/7e3c2f33-1bc0-4864-b54d-e036684522e4.jpg', 'lineQuantity': 1, 'discount': 0, 'fee': 0, 'originFee': 0, 'templateId': 91, 'templateName': '包邮', 'shopId': 1100078037, 'shopName': '光明随心订自营快递'}], 'templateId': 91, 'templateName': '包邮', 'discount': 0, 'fee': 0, 'originFee': 0, 'lineQuantitySum': 1, 'shopId': None}], 'shopId': 1100078037, 'shopName': '光明随心订自营快递', 'discount': 0, 'fee': 0, 'originFee': 0}]}, 'couponInfo': {'isVisible': True, 'unavailableList': [], 'availableList': []}, 'visibleInfo': {'invoiceInfoIsVisible': True, 'addressInfoIsVisible': True, 'buyerNoteIsVisible': True, 'couponInfoIsVisible': True, 'shoppingCardInfoVisible': True, 'mobileCheckVisible': False, 'shippingFeeIsVisible': False, 'platformActivityFeeIsVisible': True, 'shopActivityFeeIsVisible': True, 'shoppingCardFeeIsVisible': True, 'cartLinkIsVisible': True, 'memberPointsIsVisible': False, 'inviterInfoIsVisible': False, 'sellCouponIsVisible': True, 'invoiceText': None, 'invoiceIsEnable': True, 'addressInfoIsSatisfied': True, 'platformActivityInfoIsVisible': True}}],
        "extraParam": {'cartLineIds': None},
        "extra": {'orderSource': 'product.detail.page', 'settleAccountName': '上海光明随心订电子商务有限公司', 'settleAccountId': '52', 'advisorText': '光明健康顾问编号为7-8位数\\n光明健康顾问编号由字母及数字组成\\n光明健康顾问编号内字母为大写字母', 'customerName': None, 'renewOriginAddressId': '', 'devicesId': 'f7dd9fc1ac130149157842fb56a508ad', 'deviceSource': 'H5', 'customerId': None, 'renewOriginOrderId': '', 'paymentMethod': '0', 'channelName': '随心订', 'operatorType': '1', 'activityGroupId': None, 'channelCode': 'SXD', 'presentIntegralIsVisible': '1'},
        "delivery": {'code': 'express', 'deliveryTimeParam': {}},
    }

    response = session.post(url, headers=headers, json=data)

    print(response.status_code)

    return response.text

##################################################


if __name__=="__main__":

    treefrontC()

    searchStor()

    identify()

    render_ord()

    create_ord()