# -*-coding:utf-8-*-
import time
from bson import ObjectId
from flask import request
from flask_babel import gettext
from flask_login import current_user

from apps.app import mdb_web
from apps.core.flask.reqparse import arg_verify
from apps.utils.format.obj_format import json_to_pyseq, str_to_num
from apps.utils.paging.paging import datas_paging

__author__ = "Allen Woo"

def add_goods():

    '''
    添加商品
    :return:
    '''

    return update_goods_process()

def update_goods():
    '''
    更新商品
    :return:
    '''
    goods_id = request.argget.all('goods_id')
    s, r = arg_verify([(gettext("goods_id"), goods_id)], required=True)
    if not s:
        return r
    return update_goods_process(id=goods_id)

def update_goods_process(id=None):

    '''
    货物更新
    :return:
    '''
    goods_type_id = request.argget.all('goods_type_id')
    business_id = request.argget.all('business_id')
    customize_id = request.argget.all('customize_id')
    time_to_market = str_to_num(request.argget.all('time_to_market',0))
    category_id = request.argget.all('category_id')
    gender = request.argget.all('gender', "n")
    introduction = request.argget.all('introduction',"")

    s, r = arg_verify([(gettext("customize id"), customize_id)], required=True)
    if not s:
        return r

    s, r = arg_verify([(gettext("goods type"), goods_type_id)], required=True)
    if not s:
        return r
    s, r = arg_verify([(gettext("category"), category_id)], required=True)
    if not s:
        return r
    user_id = current_user.str_id
    data = {
        "goods_type_id":goods_type_id,
        "business_id":business_id,
        "customize_id":customize_id,
        "time_to_market":time_to_market,
        "category_id":category_id,
        "gender":gender,
        "introduction":introduction,
        "user_id":user_id
    }
    if id:
        data["update_time"] = time.time()
        if mdb_web.dbs["plug_warehouse_goods"].find_one({"goods_type_id":goods_type_id,"business_id": business_id,
                                                      "category_id": category_id,"customize_id": customize_id,
                                                         "user_id":user_id,
                                                        "_id": {"$ne": ObjectId(id)}}):
            # 存在相同的id
            data = {"msg": gettext("Goods ID already exists"), "msg_type": "w", "http_status": 403}
        else:
            mdb_web.dbs["plug_warehouse_goods"].update_one({"_id":ObjectId(id)},{"$set":data})
            data = {"msg": gettext("Update information succeeded"), "msg_type": "s", "http_status": 201}
    else:
        data["imgs"] = {}
        data["time"] = time.time()
        data["property"] = {}
        data["cloth"] = {}
        if mdb_web.dbs["plug_warehouse_goods"].find_one({"customize_id": customize_id,"goods_type_id":goods_type_id,
                                                      "business_id": business_id,"user_id":user_id,
                                                         "category_id": category_id}):
            # 存在相同的id
            data = {"msg": gettext("Goods ID already exists"), "msg_type": "w", "http_status": 403}
        else:
            r = mdb_web.dbs["plug_warehouse_goods"].insert(data)
            data = {"msg": gettext("Add goods successfully"), "msg_type": "s", "http_status": 201,
                    "insered_id":str(r)}
    return data


def update_property():
    '''
    更新属性
    :return:
    '''
    goods_id = request.argget.all('goods_id')
    property_name = request.argget.all('property_name')
    value = json_to_pyseq(request.argget.all('value', []))

    s, r = arg_verify([(gettext("goods_id"), goods_id),(gettext("property name"), property_name)],
                      required=True)
    if not s:
        return r

    goods = mdb_web.dbs["plug_warehouse_goods"].find_one({"_id": ObjectId(goods_id)})
    if not goods:
        data = {"msg": gettext("There is no goods"), "msg_type": "w", "http_status": 400}
        return data

    colors = []
    sizes = []
    property = goods["property"]
    for v in property.values():
        sizes.append(v["size"])
        colors.append(v["color"])
    sizes = list(set(sizes))
    colors = list(set(colors))
    property_keys = property.keys()

    if property_name == "color":
        if not sizes:
            sizes = ["" for i in range(0, len(value))]
        if not value:
            value = ["" for i in range(0, len(sizes))]
        for size in sizes:
            for c in value:
                if c in colors:
                    colors.remove(c)
                key = "{}__{}".format(c,size)
                if key not in property_keys:
                    property[key] = {"color":c, "size":size, "quantity":0, "unit_price":0,
                                     "purchase": 0, "sales": 0}

        # 删除不存在
        for c in colors:
            for size in sizes:
                key = "{}__{}".format(c, size)
                del property[key]

    elif property_name == "size":
        if not colors:
            colors = ["" for i in range(0, len(value))]
        if not value:
            value = ["" for i in range(0, len(colors))]

        property_keys = property.keys()
        for c in colors:
            for size in value:
                if size in sizes:
                    sizes.remove(size)
                key = "{}__{}".format(c,size)
                if key not in property_keys:
                    property[key] = {"color":c, "size":size, "quantity":0, "unit_price":0,
                                     "purchase":0, "sales":0}
        # 删除不存在
        for c in colors:
            for size in sizes:
                key = "{}__{}".format(c, size)
                del property[key]

    elif property_name == "other" and value:

        try:
            unit_price = float(value["unit_price"])
            quantity = int(value["quantity"])
        except:
            data = {"msg": gettext("Quantity and price must be Numbers"), "msg_type": "w",
                    "http_status": 400}
            return data

        key = value.get("key")
        if key:
            try:
                purchase = quantity - property[key]['quantity']
                property[key]['unit_price'] = unit_price
                property[key]['quantity'] = quantity
                # 计算进货数量, 销量不在此计算
                property[key]['purchase'] += purchase
                mdb_web.dbs["plug_warehouse_goods_sales"].insert({
                    "user_id": current_user.str_id,
                    "goods_id": goods_id,
                    "size": property[key]['size'],
                    "color": property[key]['color'],
                    "purchase": purchase,
                    "time": time.time()
                })

            except:
                data = {"msg": gettext("Quantity and price must be Numbers"), "msg_type": "w",
                        "http_status": 400}
                return data
        else:
            # 全部修改
            for key in property_keys:
                purchase = quantity - property[key]['quantity']
                property[key]['unit_price'] = unit_price
                property[key]['quantity'] = quantity
                # 计算进货数量, 销量不在此计算
                property[key]['purchase'] += purchase
                mdb_web.dbs["plug_warehouse_goods_sales"].insert({
                    "user_id": current_user.str_id,
                    "goods_id": goods_id,
                    "size": property[key]['size'],
                    "color": property[key]['color'],
                    "purchase": purchase,
                    "time": time.time()
                })


    mdb_web.dbs["plug_warehouse_goods"].update_one({"_id": ObjectId(goods_id)},
                                                {"$set":{"property":property, "update_time":time.time()}})
    data = {"msg": gettext("Update {} succeeded".format(property_name)), "msg_type": "s", "http_status": 201}
    return data


def update_cloth():
    '''
    更新成分
    :return:
    '''
    goods_id = request.argget.all('goods_id')
    value = json_to_pyseq(request.argget.all('value', []))

    s, r = arg_verify([(gettext("goods_id"), goods_id)],
                      required=True)
    if not s:
        return r

    goods = mdb_web.dbs["plug_warehouse_goods"].find_one({"_id": ObjectId(goods_id)})
    if not goods:
        data = {"msg": gettext("There is no goods"), "msg_type": "w", "http_status": 400}
        return data

    cloth_names = list(goods["cloth"].keys())
    if value:
        total = 0
        for v in value:
            if v["name"] in cloth_names:
                cloth_names.remove(v["name"])
            try:
                per = float(v["per"])
                if per > 0:
                    goods["cloth"][v["name"]] = float(v["per"])
                    total += per
            except:
                data = {"msg": gettext("The proportion of ingredients must be a number"), "msg_type": "w",
                        "http_status": 400}
                return data
        if total>100:
            data = {"msg": gettext("The proportion of ingredients is greater than 100%"), "msg_type": "w",
                    "http_status": 403}
            return data
    # 删除不需要的
    for k in cloth_names:
        del goods["cloth"][k]
    mdb_web.dbs["plug_warehouse_goods"].update_one({"_id": ObjectId(goods_id)},
                                                {"$set":{"cloth":goods["cloth"]}})
    data = {"msg": gettext("Update cloth succeeded"), "msg_type": "s", "http_status": 201}
    return data

def get_goods():

    '''
    获取一个货物信息
    :return:
    '''
    goods_id = request.argget.all('goods_id')
    goods = mdb_web.dbs["plug_warehouse_goods"].find_one({"_id": ObjectId(goods_id),
                                                          "user_id":current_user.str_id},
                                                         {"_id":0})
    if goods:
        sizes = []
        colors = []
        cloths = []
        total = 0
        shortcoming = 0
        total_sales = 0
        inventory_warning = 0
        property = goods["property"]
        for v in property.values():
            if v["size"]:
                sizes.append(v["size"])
            if v["color"]:
                colors.append(v["color"])
            if v["quantity"] > 0:
                total += v["quantity"]
            elif v["quantity"] < 0:
                shortcoming += -v["quantity"]
            total_sales+=v["sales"]
            if v["quantity"] < 10:
                inventory_warning += 1
        for k,v in goods['cloth'].items():
            cloths.append({"name":k, "per":v})

        sizes = list(set(sizes))
        colors = list(set(colors))
        goods["sizes"] = sizes
        goods["colors"] = colors
        goods["cloths"] = cloths
        goods["total"] = total
        goods["total_sales"] = total_sales
        goods["inventory_warning"] = inventory_warning
        goods["shortcoming"] = shortcoming

        data = {"goods":goods, "msg_type": "s", "http_status": 200}
    else:
        data = {"msg": gettext("No related data found"), "msg_type": "w", "http_status": 404}
    return data

def get_more_goods():

    '''
    获取多个货物信息
    :return:
    '''
    goods_type_id = request.argget.all('goods_type_id')
    category_id = request.argget.all('category_id')
    business_id = request.argget.all('business_id')
    keyword = request.argget.all('keyword')
    sort = json_to_pyseq(request.argget.all('sort',[("update_time", -1)]))
    page = str_to_num(request.argget.all('page', 1))
    pre = str_to_num(request.argget.all('pre', 15))

    query = {"goods_type_id":goods_type_id, "user_id":current_user.str_id}
    if category_id:
        query["category_id"] = category_id
    if business_id:
        query["business_id"] = business_id
    if keyword:
        keyword = {"$regex":r".*{}.*".find(keyword)}
        query["$or"] = [{"customize_id":keyword},
                        {"introduction": keyword},
                        {"property.color": keyword},
                        ]

    goods = mdb_web.dbs["plug_warehouse_goods"].find(query)
    data_cnt = goods.count(True)
    if data_cnt:
        goods = list(goods.sort(sort).skip(pre * (page - 1)).limit(pre))
        goods = datas_paging(pre=pre, page_num=page, data_cnt=data_cnt, datas=goods)
        for gd in goods["datas"]:
            sizes = []
            colors = []
            cloths = []
            total = 0
            shortcoming = 0
            total_sales = 0
            inventory_warning = 0
            property = gd["property"]
            for v in property.values():
                if v["size"]:
                    sizes.append(v["size"])
                if v["color"]:
                    colors.append(v["color"])
                if v["quantity"]>0:
                    total += v["quantity"]
                elif v["quantity"]<0:
                    shortcoming += -v["quantity"]
                total_sales += v["sales"]
                if v["quantity"] < 10:
                    inventory_warning += 1

            for k, v in gd['cloth'].items():
                cloths.append({"name": k, "per": v})

            sizes = list(set(sizes))
            colors = list(set(colors))
            gd["sizes"] = sizes
            gd["colors"] = colors
            gd["cloths"] = cloths
            gd["total"] = total
            gd["total_sales"] = total_sales
            gd["_id"] = str(gd["_id"])
            gd["inventory_warning"] = inventory_warning
            gd["shortcoming"] = shortcoming

        data = {"goods":goods, "msg_type": "s", "http_status": 200}
    else:
        data = {"msg": gettext("No related data found"), "msg_type": "w", "http_status": 404}
    return data

def del_goods():

    '''
    删除
    :return:
    '''
    ids = json_to_pyseq(request.argget.all('ids'))
    s, r = arg_verify([(gettext("ids"), ids)], required=True)
    if not s:
        return r
    user_id = current_user.str_id
    obj_ids = []
    for id in ids:
        obj_ids.append(ObjectId(id))
    r = mdb_web.dbs["plug_warehouse_goods"].delete_many({"_id": {"$in": obj_ids}, "user_id":user_id})
    if r.deleted_count:
        data = {"msg": gettext("Successfully deleted {} goods").format(r.deleted_count), "msg_type": "s",
                "http_status": 204}
    else:
        data = {"msg": gettext("Failed to delete"), "msg_type": "w", "http_status": 400}
    return data