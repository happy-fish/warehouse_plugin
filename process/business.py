# -*-coding:utf-8-*-
from bson import ObjectId
from flask import request
from flask_babel import gettext
from flask_login import current_user

from apps.app import mdb_web
from apps.core.flask.reqparse import arg_verify
from apps.utils.format.obj_format import objid_to_str, json_to_pyseq

__author__ = "Allen Woo"


def get_businesses():

    '''
    获取所有厂家
    :return:
    '''
    goods_type_id = request.argget.all('goods_type_id')
    business = mdb_web.dbs["plug_warehouse_business"].find({"type_id":goods_type_id,
                                                          "user_id":current_user.str_id})
    business = objid_to_str(business)
    data = {"businesses":business, "msg_type": "s", "msg":gettext("Successful data acquisition"),
            "http_status": 200}

    return data

def add_business():

    '''
    添加厂家
    :return:
    '''
    goods_type_id = request.argget.all('goods_type_id')
    mobile_phone = request.argget.all('mobile_phone')
    addr = request.argget.all('addr')
    name = request.argget.all('name')
    s, r = arg_verify([(gettext("name"), name), (gettext("goods_type_id"), goods_type_id)],
                      required=True)
    if not s:
        return r

    user_id = current_user.str_id
    if mdb_web.dbs["plug_warehouse_business"].find_one({"name":name, "type_id":goods_type_id,"user_id":user_id}):
        data = {"msg": gettext("business already exists"), "msg_type": "w", "http_status": 403}
    else:
        up_data = {
            "name": name,
            "type_id":goods_type_id,
            "mobile_phone":mobile_phone,
            "addr":addr,
            "user_id": user_id
        }
        mdb_web.dbs["plug_warehouse_business"].insert(up_data)
        data = {"msg": gettext("Add business successfully"), "msg_type": "s", "http_status": 201}

    return data

def update_business():

    '''
    更新厂家名称
    :return:
    '''
    name = request.argget.all('name')
    mobile_phone = request.argget.all('mobile_phone')
    addr = request.argget.all('addr')
    goods_type_id = request.argget.all('goods_type_id')
    id = request.argget.all('id')
    s, r = arg_verify([(gettext("name"), name), ("id", id)], required=True)
    if not s:
        return r
    user_id = current_user.str_id
    if mdb_web.dbs["plug_warehouse_business"].find_one({"name":name, "user_id":user_id,"type_id":goods_type_id,
                                                 "_id":{"$ne":ObjectId(id)}}):
        data = {"msg": gettext("Business already exists"), "msg_type": "w", "http_status": 403}
    else:
        up_data = {
            "name": name,
            "mobile_phone": mobile_phone,
            "addr": addr,
        }
        print(up_data)
        mdb_web.dbs["plug_warehouse_business"].update_one({"_id":ObjectId(id), "user_id":current_user.str_id},
                                                   {"$set":up_data})
        data = {"msg": gettext("Update business successfully"), "msg_type": "s", "http_status": 201}

    return data

def del_business():

    '''
    删除厂家
    :return:
    '''
    ids = json_to_pyseq(request.argget.all('ids'))
    s, r = arg_verify([(gettext("ids"), ids)], required=True)
    if not s:
        return r
    user_id = current_user.str_id
    obj_ids = []
    faied_cnt = 0
    for id in ids:
        if mdb_web.dbs["plug_warehouse_goods"].find_one({"business_id":id, "user_id":user_id}):
            faied_cnt += 1
            continue
        obj_ids.append(ObjectId(id))

    r = mdb_web.dbs["plug_warehouse_business"].delete_many({"_id": {"$in": obj_ids}, "user_id":user_id})
    if r.deleted_count:
        data = {"msg": gettext("Successfully deleted {} business").format(r.deleted_count), "msg_type": "s",
                "http_status": 204}
    else:
        data = {"msg": gettext("Failed to delete"), "msg_type": "w", "http_status": 400}

    if faied_cnt:
        data["msg"] = gettext("There are {} business below the goods, can not be deleted, can not be deleted").format(faied_cnt)
    return data