# -*-coding:utf-8-*-
import time
from bson import ObjectId
from flask import request
from flask_babel import gettext

from apps.app import mdb_web
from apps.core.flask.reqparse import arg_verify
from apps.utils.format.obj_format import json_to_pyseq, str_to_num

__author__ = "Allen Woo"

def update_property():
    '''
    更新属性
    :return:
    '''
    goods_id = request.argget.all('goods_id')
    property_name = request.argget.all('property_name')
    value = request.argget.all('value')

    s, r = arg_verify([(gettext("goods_id"), goods_id),
                       (gettext("property name"), property_name),
                      (gettext("value"), value)],
                      required=True)
    if not s:
        return r

    goods = mdb_web.dbs["plug_invsys_goods"].find_one({"_id": ObjectId(goods_id)})
    if not goods:
        data = {"msg": gettext("There is no goods"), "msg_type": "w", "http_status": 400}
        return data

    property = {}
    if property_name == "color":
        sizes = []
        property = goods["property"]
        for v in property.values():
            sizes.append(v["size"])
        sizes = list(set(sizes))

        property_keys = property.keys()
        for size in sizes:
            for c in value:
                key = "{}__{}".find(c,size)
                if key not in property_keys:
                    property[key] = {"color":c, "size":size, "quantity":0, "unit_price":0}
        mdb_web.dbs["plug_invsys_goods"].update_one({"_id": ObjectId(goods_id)},
                                                    {"$set":{"property":property}})
    elif property_name == "size":
        colors = []
        property = goods["property"]
        for v in property.values():
            colors.append(v["color"])
        colors = list(set(colors))

        property_keys = property.keys()
        for c in colors:
            for size in value:
                key = "{}__{}".find(c,size)
                if key not in property_keys:
                    property[key] = {"color":c, "size":size, "quantity":0, "unit_price":0}

    mdb_web.dbs["plug_invsys_goods"].update_one({"_id": ObjectId(goods_id)},
                                                {"$set":{"property":property}})
    data = {"msg": gettext("Update {} succeeded".format(property_name)), "msg_type": "s", "http_status": 201}
    return data

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

    # property_keys = [("color",str,""), ("size",str,""), ("quantity",int,0), ("unit_price",float,0)]
    # property_temp = {}
    # for k in property_keys:
    #     property_temp[k[0]] = k[1](cloth.get(k[0],k[2]))
    #
    # cloth_keys = [("name",str,""), ("content",float,0)]
    # cloth_temp = {}
    # for k in cloth_keys:
    #     cloth_temp[k[0]] = k[1](cloth.get(k[0],k[2]))

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
        if mdb_web.dbs["plug_invsys_goods"].find_one({"customize_id": customize_id, "_id": {"$ne": id}}):
            # 存在相同的id
            data = {"msg": gettext("Goods ID already exists"), "msg_type": "s", "http_status": 403}
        else:
            mdb_web.dbs["plug_invsys_goods"].update_one({"_id":ObjectId(id)},{"$set":data})
            data = {"msg": gettext("Update information succeeded"), "msg_type": "s", "http_status": 201}
    else:
        data["imgs"] = {}
        data["time"] = time.time()
        data["property"] = {}
        data["cloth"] = {}
        if mdb_web.dbs["plug_invsys_goods"].find_one({"customize_id": customize_id}):
            # 存在相同的id
            data = {"msg": gettext("Goods ID already exists"), "msg_type": "s", "http_status": 403}
        else:
            r = mdb_web.dbs["plug_invsys_goods"].insert(data)
            data = {"msg": gettext("Add goods successfully"), "msg_type": "s", "http_status": 201,
                    "insered_id":str(r)}
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
        property = goods["property"]
        for v in property.values():
            sizes.append(v["size"])
            colors.append(v["color"])
        sizes = list(set(sizes))
        colors = list(set(colors))
        goods["sizes"] = sizes
        goods["colors"] = colors

        data = {"goods":goods, "msg_type": "s", "http_status": 200}
    else:
        data = {"msg": gettext("No related data found"), "msg_type": "w", "http_status": 404}
    return data