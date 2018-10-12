# -*-coding:utf-8-*-
import time
from bson import ObjectId
from flask import request
from flask_babel import gettext
from flask_login import current_user

from apps.app import mdb_web
from apps.core.flask.reqparse import arg_verify
from apps.utils.format.obj_format import str_to_num, json_to_pyseq

__author__ = "Allen Woo"

def update_quantity():
    '''
    更新销量
    :return:
    '''
    goods_id = request.argget.all('goods_id')
    value = json_to_pyseq(request.argget.all('value', {}))
    modify_op = request.argget.all('modify_op')

    s, r = arg_verify([(gettext("goods_id"), goods_id),
                       (gettext("modify_op"), modify_op)],
                      required=True)
    if not s:
        return r

    goods = mdb_web.dbs["plug_warehouse_goods"].find_one({"_id": ObjectId(goods_id)})
    if not goods:
        data = {"msg": gettext("There is no goods"), "msg_type": "w", "http_status": 400}
        return data

    property = goods["property"]
    property_keys = property.keys()
    key = value.get("key")
    if key not in property_keys:
        data = {"msg": gettext("Without this attribute"), "msg_type": "w", "http_status": 400}
        return data

    if modify_op == "sell":
        quantity = int(value.get("quantity", 0))
        property[key]['quantity'] -= quantity
        property[key]['sales'] += quantity
        mdb_web.dbs["plug_warehouse_goods_sales"].insert({
            "user_id":current_user.str_id,
            "goods_id":goods_id,
            "size":property[key]['size'],
            "color": property[key]['color'],
            "sales":quantity,
            "time":time.time()
        })

    elif modify_op == "add":
        quantity = int(value.get("quantity", 0))
        property[key]['quantity'] += quantity
        property[key]['purchase'] += quantity

        mdb_web.dbs["plug_warehouse_goods_sales"].insert({
            "user_id": current_user.str_id,
            "goods_id": goods_id,
            "size": property[key]['size'],
            "color": property[key]['color'],
            "purchase": quantity,
            "time": time.time()
        })


    mdb_web.dbs["plug_warehouse_goods"].update_one({"_id": ObjectId(goods_id)},
                                                {"$set":{"property":property, "update_time":time.time()}})
    data = {"msg": gettext("Update succeeded"), "msg_type": "s", "http_status": 201}
    return data