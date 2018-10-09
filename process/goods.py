# -*-coding:utf-8-*-
import time
from bson import ObjectId
from flask import request
from flask_babel import gettext

from apps.app import mdb_web
from apps.core.flask.reqparse import arg_verify
from apps.utils.format.obj_format import json_to_pyseq, str_to_num, objid_to_str

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

    data = {
        "goods_type_id":goods_type_id,
        "business_id":business_id,
        "customize_id":customize_id,
        "time_to_market":time_to_market,
        "category_id":category_id,
        "gender":gender,
        "introduction":introduction,
    }
    if id:
        data["update_time"] = time.time()
        if mdb_web.dbs["plug_invsys_goods"].find_one({"goods_type_id":goods_type_id,"business_id": business_id,
                                                      "category_id": category_id,"customize_id": customize_id,
                                                        "_id": {"$ne": ObjectId(id)}}):
            # 存在相同的id
            data = {"msg": gettext("Goods ID already exists"), "msg_type": "w", "http_status": 403}
        else:
            mdb_web.dbs["plug_invsys_goods"].update_one({"_id":ObjectId(id)},{"$set":data})
            data = {"msg": gettext("Update information succeeded"), "msg_type": "s", "http_status": 201}
    else:
        data["imgs"] = {}
        data["time"] = time.time()
        data["property"] = {}
        data["cloth"] = {}
        if mdb_web.dbs["plug_invsys_goods"].find_one({"customize_id": customize_id,"goods_type_id":goods_type_id,
                                                      "business_id": business_id,"category_id": category_id}):
            # 存在相同的id
            data = {"msg": gettext("Goods ID already exists"), "msg_type": "w", "http_status": 403}
        else:
            r = mdb_web.dbs["plug_invsys_goods"].insert(data)
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

    goods = mdb_web.dbs["plug_invsys_goods"].find_one({"_id": ObjectId(goods_id)})
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
                    property[key] = {"color":c, "size":size, "quantity":0, "unit_price":0}

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
                    property[key] = {"color":c, "size":size, "quantity":0, "unit_price":0}
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
                property[key]['unit_price'] = unit_price
                property[key]['quantity'] = quantity
            except:
                data = {"msg": gettext("Quantity and price must be Numbers"), "msg_type": "w",
                        "http_status": 400}
                return data
        else:
            # 全部修改
            for k in property_keys:
                property[k]['unit_price'] = unit_price
                property[k]['quantity'] = quantity

    mdb_web.dbs["plug_invsys_goods"].update_one({"_id": ObjectId(goods_id)},
                                                {"$set":{"property":property}})
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

    goods = mdb_web.dbs["plug_invsys_goods"].find_one({"_id": ObjectId(goods_id)})
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
    mdb_web.dbs["plug_invsys_goods"].update_one({"_id": ObjectId(goods_id)},
                                                {"$set":{"cloth":goods["cloth"]}})
    data = {"msg": gettext("Update cloth succeeded"), "msg_type": "s", "http_status": 201}
    return data

def get_goods():

    '''
    获取一个货物信息
    :return:
    '''
    goods_id = request.argget.all('goods_id')
    goods = mdb_web.dbs["plug_invsys_goods"].find_one({"_id": ObjectId(goods_id)}, {"_id":0})
    if goods:
        sizes = []
        colors = []
        cloths = []
        total = 0
        property = goods["property"]
        for v in property.values():
            if v["size"]:
                sizes.append(v["size"])
            if v["color"]:
                colors.append(v["color"])
            total+=v["quantity"]
        for k,v in goods['cloth'].items():
            cloths.append({"name":k, "per":v})

        sizes = list(set(sizes))
        colors = list(set(colors))
        goods["sizes"] = sizes
        goods["colors"] = colors
        goods["cloths"] = cloths
        goods["total"] = total

        data = {"goods":goods, "msg_type": "s", "http_status": 200}
    else:
        data = {"msg": gettext("No related data found"), "msg_type": "w", "http_status": 404}
    return data

def get_more_goods():

    '''
    获取多个货物信息
    :return:
    '''
    #category_id = request.argget.all('category_id')
    goods = mdb_web.dbs["plug_invsys_goods"].find({})
    if goods.count(True):
        goods = list(goods)
        for gd in goods:
            sizes = []
            colors = []
            cloths = []
            total = 0
            property = gd["property"]
            for v in property.values():
                if v["size"]:
                    sizes.append(v["size"])
                if v["color"]:
                    colors.append(v["color"])
                total += v["quantity"]
            for k, v in gd['cloth'].items():
                cloths.append({"name": k, "per": v})

            sizes = list(set(sizes))
            colors = list(set(colors))
            gd["sizes"] = sizes
            gd["colors"] = colors
            gd["cloths"] = cloths
            gd["total"] = total
            gd["_id"] = str(gd["_id"])
        data = {"goods":goods, "msg_type": "s", "http_status": 200}
    else:
        data = {"msg": gettext("No related data found"), "msg_type": "w", "http_status": 404}
    return data