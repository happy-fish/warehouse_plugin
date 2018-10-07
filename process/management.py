# -*-coding:utf-8-*-
from bson import ObjectId
from flask import request
from flask_babel import gettext

from apps.app import mdb_web
from apps.core.flask.reqparse import arg_verify
from apps.utils.format.obj_format import json_to_pyseq

__author__ = "Allen Woo"

def add_goods():

    '''
    添加商品
    :return:
    '''
    update_goods_process()

def update_goods():
    '''
    更新商品
    :return:
    '''
    goods_id = request.argget.all('goods_id')
    s, r = arg_verify([(gettext("goods_id"), goods_id)], required=True)
    if not s:
        return r
    update_goods_process(id=goods_id)

def update_goods_process(id=None):

    '''
    货物更新
    :return:
    '''
    goods_type = request.argget.all('goods_type_id')
    business_id = request.argget.all('business_id')
    customize_id = request.argget.all('customize_id')
    property = json_to_pyseq(request.argget.all('property')) # 属性
    time_to_market = request.argget.all('time_to_market')
    category_id = request.argget.all('category_id')
    gender = request.argget.all('gender', "n")
    cloth = json_to_pyseq(request.argget.all('cloth'))
    introduction = request.argget.all('introduction',"")

    s, r = arg_verify([(gettext("goods type"), goods_type)], required=True)
    if not s:
        return r

    s, r = arg_verify([(gettext("category"), category_id)], required=True)
    if not s:
        return r

    s, r = arg_verify([(gettext("property"), property)], need_type=dict)
    if not s:
        return r

    property_keys = [("color",str,""), "size",str,"", "quantity",int,0, "unit_price",float,0]
    property_temp = {}
    for k in property_keys:
        property_temp[k] = k[1](cloth.get(k[0],k[2]))

    cloth_keys = [("name",str,""), ("content",float,0)]
    cloth_temp = {}
    for k in cloth_keys:
        cloth_temp[k] = k[1](cloth.get(k[0],k[2]))

    data = {
        goods_type:goods_type,
        business_id:business_id,
        customize_id:customize_id,
        property:property_temp,
        time_to_market:time_to_market,
        category_id:category_id,
        gender:gender,
        cloth:cloth,
        introduction:introduction
    }

    if id:
        if mdb_web.dbs["plug_invsys_goods"].find_one({"customize_id": customize_id, "_id": {"$ne": id}}):
            # 存在相同的id
            data = {"msg": gettext("Goods ID already exists"), "msg_type": "s", "http_status": 403}
        else:
            mdb_web.dbs["plug_invsys_goods"].update_one({"_id":ObjectId(id)},{"$set":data})
            data = {"msg": gettext("Update information succeeded"), "msg_type": "s", "http_status": 201}
    else:
        data["imgs"] = {}
        if mdb_web.dbs["plug_invsys_goods"].find_one({"customize_id": customize_id}):
            # 存在相同的id
            data = {"msg": gettext("Goods ID already exists"), "msg_type": "s", "http_status": 403}
        else:
            mdb_web.dbs["plug_invsys_goods"].insert(data)
            data = {"msg": gettext("Add goods successfully"), "msg_type": "s", "http_status": 201}
    return data

def get_goods():

    '''
    获取一个货物信息
    :return:
    '''
    goods_id = request.argget.all('goods_id')
    goods = mdb_web.dbs["plug_invsys_goods"].find_one({"_id": ObjectId(goods_id)}, {"_id":0})
    if goods:
        data = {"goods":goods, "msg_type": "s", "http_status": 200}
    else:
        data = {"msg": gettext("No related data found"), "msg_type": "w", "http_status": 404}
    return data