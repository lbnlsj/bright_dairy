# API例子以及说明
## 获取列表
```js
fetch("https://m.4008117117.com/api/item/shop-category/tree?frontCategoryId=4403&longitude=120.2126&latitude=30.290851&isFinish=true", {
  "headers": {
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
    "x-requested-with": "XMLHttpRequest"
  },
  "referrer": "https://m.4008117117.com/category?firstId&id&itemId",
  "referrerPolicy": "strict-origin-when-cross-origin",
  "body": null,
  "method": "GET",
  "mode": "cors",
  "credentials": "include"
});
```
## 获取列表内内容
```js
fetch("https://m.4008117117.com/api/item/store/item/searchStoreSkuByCategory?pageNo=1&pageSize=500&frontCategoryId=8329&longitude=120.2126&latitude=30.290851&isFinish=true", {
  "headers": {
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
    "x-requested-with": "XMLHttpRequest"
  },
  "referrer": "https://m.4008117117.com/category?firstId&id&itemId",
  "referrerPolicy": "strict-origin-when-cross-origin",
  "body": null,
  "method": "GET",
  "mode": "cors",
  "credentials": "include"
});
```
## 登陆
```js
fetch("https://m.4008117117.com/api/user/web/login/identify", {
  "headers": {
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
    "x-requested-with": "XMLHttpRequest"
  },
  "referrer": "https://m.4008117117.com/login?from=%7B%22routeName%22%3A%22ItemDetail%22%2C%22params%22%3A%7B%22itemId%22%3A110005200318001%2C%22storeId%22%3A1100078037%2C%22isO2O%22%3Afalse%2C%22name%22%3A%22%E7%AB%8B%E5%8D%B3%E8%B4%AD%E4%B9%B0%22%2C%22for%22%3A%22login%22%7D%7D",
  "referrerPolicy": "strict-origin-when-cross-origin",
  "body": "{\"password\":\"gbaycm123\",\"identify\":\"15557581380\",\"isApp\":true,\"deviceId\":\"68e07a174825b8bc0ee0769ef6ee03fc\",\"deviceType\":\"H5\",\"userAgent\":\"Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36\",\"uuid\":\"1733798081506_65b8e9f97052cc46a498\",\"deviceSource\":\"344*882 devices\"}",
  "method": "POST",
  "mode": "cors",
  "credentials": "include"
});
```

## render-order
```js
fetch("https://m.4008117117.com/api/trade/buy/render-order", {
  "headers": {
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
    "x-requested-with": "XMLHttpRequest"
  },
  "referrer": "https://m.4008117117.com/buyer/preorder?from=itemDetail&itemId=110005200318001&itemName=%E9%9A%8F%E5%B0%8F%E8%AE%A2%E6%98%9F%E5%BA%A7%E6%8C%82%E4%BB%B6--%E5%8F%8C%E5%AD%90%E5%BA%A7&storeId=1100078037&type=shop",
  "referrerPolicy": "strict-origin-when-cross-origin",
  "body": "{\"deviceSource\":\"H5\",\"orderSource\":\"product.detail.page\",\"buyConfig\":{\"lineGrouped\":true,\"multipleCoupon\":true},\"itemName\":\"随小订星座挂件--双子座\",\"orderLineList\":[{\"skuId\":110005200318001,\"itemId\":110005200318001,\"quantity\":1,\"promotionTag\":null,\"activityId\":null,\"extra\":{},\"shopId\":1100078037}],\"divisionIds\":\"110000,110100,110105\",\"addressId\":null,\"couponParams\":[],\"benefitParams\":[],\"delivery\":{},\"extra\":{\"renewOriginOrderId\":\"\",\"renewOriginAddressId\":\"\",\"activityGroupId\":null},\"devicesId\":\"f7dd9fc1ac130149157842fb56a508ad\"}",
  "method": "POST",
  "mode": "cors",
  "credentials": "include"
});
```

## create-order
```js
fetch("https://m.4008117117.com/api/trade/buy/create-order", {
  "headers": {
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
    "x-requested-with": "XMLHttpRequest"
  },
  "referrer": "https://m.4008117117.com/buyer/preorder?from=itemDetail&itemId=110005200318001&itemName=%E9%9A%8F%E5%B0%8F%E8%AE%A2%E6%98%9F%E5%BA%A7%E6%8C%82%E4%BB%B6--%E5%8F%8C%E5%AD%90%E5%BA%A7&storeId=1100078037&type=shop",
  "referrerPolicy": "strict-origin-when-cross-origin",
  "body": "{\"deviceSource\":\"H5\",\"orderSource\":\"product.detail.page\",\"buyConfig\":{\"lineGrouped\":true,\"multipleCoupon\":true},\"memberPointsDeductionInfo\":{\"available\":false,\"visible\":false,\"point\":0,\"chosenIntegral\":0,\"maxExchangeValue\":0,\"minExchangeValue\":100,\"exchangeUnit\":100,\"deductAmount\":0,\"exchangeRatio\":1,\"displayRemark\":null,\"extra\":null,\"presentIntegral\":29},\"itemName\":\"随小订星座挂件--双子座\",\"mobile\":null,\"invoice\":null,\"addressId\":32189953,\"couponParams\":[{\"activityId\":-1,\"benefitId\":null,\"shopId\":0},{\"activityId\":-1,\"benefitId\":null,\"shopId\":1100078037}],\"benefitParams\":[{\"activityId\":-1,\"benefitId\":null,\"shopId\":0,\"benefitType\":null,\"amount\":null}],\"orderList\":[{\"activityOrderList\":[{\"activityMatchedLine\":{\"activity\":null,\"valid\":false,\"benefitId\":null,\"benefitUsageInfo\":null,\"display\":null,\"matchedLineIds\":null,\"errorMsg\":null},\"activityExist\":false,\"orderLineList\":null,\"orderLineGroups\":[{\"orderLineList\":[{\"itemId\":110005200318001,\"skuId\":110005200318001,\"skuCode\":\"goods1134\",\"bundleId\":null,\"quantity\":1,\"activityId\":null,\"shopActivityId\":null,\"extraParam\":null,\"promotionTag\":null,\"shopId\":1100078037,\"lineId\":\"110005200318001_1100078037\",\"categoryId\":1514,\"skuName\":\"随小订星座挂件--双子座\",\"attrs\":[{\"attrVal\":\"63g*1\",\"attrKey\":\"规格\"}],\"mainImage\":\"https://assets.4008117117.com/upload/2021/6/28/7e3c2f33-1bc0-4864-b54d-e036684522e4.jpg\",\"outerSkuCode\":null,\"status\":1,\"salePrice\":2900,\"preferSalePrice\":2900,\"extra\":{\"devicesId\":\"f7dd9fc1ac130149157842fb56a508ad\",\"fullUnit\":\"63g*1\",\"itemType\":\"1\",\"shopType\":null,\"deliveryTimeType\":null,\"businessCode\":\"express\",\"businessName\":\"快递\",\"businessType\":\"1\",\"unitQuantity\":\"1\",\"categoryList\":\"[1514,1508]\"},\"summary\":{\"deposit\":null,\"balanceDue\":null,\"taxFee\":0,\"summary\":2900,\"skuFee\":2900},\"bizCode\":\"express\",\"itemAttributes\":{\"saleUnitName\":null,\"grossWeight\":\"63\",\"fullUnit\":\"63g*1\",\"innerProduct\":\"true\",\"erpCode\":\"11190105\",\"categoryList\":\"[1514,1508]\",\"weight\":\"63\",\"frontCategoryIdList\":\"[4161,4162,4835,4100,4836,4101,4837,5029,5030,5031,3571,3572,8212,3573,3574,8346,8348]\",\"skuCode\":\"goods1134\",\"updatedAt\":\"1719759871000\"}}]}]}],\"shop\":{\"tenantId\":null,\"tenantIdLong\":null,\"extra\":{\"shipper\":\"null\",\"clearable\":\"0\",\"erpAccountCode\":\"1201\",\"priceTemplateId\":\"1000000000330\",\"sellerName\":\"上海光明随心订电子商务有限公司\",\"supportDelivery\":\"1\",\"defaultDeliveryTemplateId\":\"91\",\"organizationId\":\"20406\",\"supportPickUp\":\"0\",\"sellerId\":\"52\",\"shopType\":\"4\",\"settlementSubjectId\":\"52\",\"updatedAt\":\"1728890571000\"},\"id\":1100078037,\"outerId\":\"1100078037\",\"userId\":52,\"userName\":null,\"name\":\"光明随心订自营快递\",\"status\":1,\"type\":1,\"phone\":null,\"businessId\":52,\"imageUrl\":null,\"address\":null,\"email\":null,\"tags\":null,\"buyerNote\":null,\"businessType\":7201},\"buyerNote\":null,\"extraParam\":null,\"priceInfo\":{\"allDiscount\":0,\"couponTotal\":0,\"shopDiscountFee\":0,\"platformDiscountFee\":0,\"benefitDiscountFee\":0,\"totalTaxFee\":0,\"skuTotalFee\":2900,\"skuOriginTotalFee\":2900,\"shipFeeTotal\":0,\"inviterTotalFee\":0,\"memberPointDeductTotal\":0,\"sellCouponTotalFee\":0,\"nonCouponTotal\":0,\"totalFee\":2900},\"shipFeeInfo\":{\"visible\":false,\"shipFeeDiscount\":0,\"shipFeeTotal\":0,\"shipFeeOriginTotal\":0,\"shipFeeDetailList\":[{\"shipFeeTemplateList\":[{\"shipFeeLineList\":[{\"lineId\":\"110005200318001_1100078037\",\"skuImg\":\"https://assets.4008117117.com/upload/2021/6/28/7e3c2f33-1bc0-4864-b54d-e036684522e4.jpg\",\"lineQuantity\":1,\"discount\":0,\"fee\":0,\"originFee\":0,\"templateId\":91,\"templateName\":\"包邮\",\"shopId\":1100078037,\"shopName\":\"光明随心订自营快递\"}],\"templateId\":91,\"templateName\":\"包邮\",\"discount\":0,\"fee\":0,\"originFee\":0,\"lineQuantitySum\":1,\"shopId\":null}],\"shopId\":1100078037,\"shopName\":\"光明随心订自营快递\",\"discount\":0,\"fee\":0,\"originFee\":0}]},\"couponInfo\":{\"isVisible\":true,\"unavailableList\":[],\"availableList\":[]},\"visibleInfo\":{\"invoiceInfoIsVisible\":true,\"addressInfoIsVisible\":true,\"buyerNoteIsVisible\":true,\"couponInfoIsVisible\":true,\"shoppingCardInfoVisible\":true,\"mobileCheckVisible\":false,\"shippingFeeIsVisible\":false,\"platformActivityFeeIsVisible\":true,\"shopActivityFeeIsVisible\":true,\"shoppingCardFeeIsVisible\":true,\"cartLinkIsVisible\":true,\"memberPointsIsVisible\":false,\"inviterInfoIsVisible\":false,\"sellCouponIsVisible\":true,\"invoiceText\":null,\"invoiceIsEnable\":true,\"addressInfoIsSatisfied\":true,\"platformActivityInfoIsVisible\":true}}],\"extraParam\":{\"cartLineIds\":null},\"extra\":{\"orderSource\":\"product.detail.page\",\"settleAccountName\":\"上海光明随心订电子商务有限公司\",\"settleAccountId\":\"52\",\"advisorText\":\"光明健康顾问编号为7-8位数\\\\n光明健康顾问编号由字母及数字组成\\\\n光明健康顾问编号内字母为大写字母\",\"customerName\":null,\"renewOriginAddressId\":\"\",\"devicesId\":\"f7dd9fc1ac130149157842fb56a508ad\",\"deviceSource\":\"H5\",\"customerId\":null,\"renewOriginOrderId\":\"\",\"paymentMethod\":\"0\",\"channelName\":\"随心订\",\"operatorType\":\"1\",\"activityGroupId\":null,\"channelCode\":\"SXD\",\"presentIntegralIsVisible\":\"1\"},\"delivery\":{\"code\":\"express\",\"deliveryTimeParam\":{}}}",
  "method": "POST",
  "mode": "cors",
  "credentials": "include"
});
```