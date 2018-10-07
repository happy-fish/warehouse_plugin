# -*-coding:utf-8-*-
from bson import ObjectId
from flask import request
from flask_babel import gettext
from flask_login import current_user

from apps.app import mdb_web
from apps.core.flask.reqparse import arg_verify
from apps.utils.format.obj_format import objid_to_str, json_to_pyseq

__author__ = "Allen Woo"


def get_goods_types():

    '''
    获取商品所有分类
    :return:
    '''

    types = mdb_web.dbs["plug_invsys_type"].find({"user_id": current_user.str_id})
    types = objid_to_str(types)
    data = {"types": types, "msg_type": "s", "msg": gettext("Successful data acquisition"),
            "http_status": 200}

    return data

def add_goods_types():

    '''
    添加商品分类
    :return:
    '''
    name = request.argget.all('name')
    s, r = arg_verify([(gettext("name"), name)], required=True)
    if not s:
        return r
    user_id = current_user.str_id

    if mdb_web.dbs["plug_invsys_type"].find_one({"name":name, "user_id":user_id}):
        data = {"msg": gettext("Item type already exists"), "msg_type": "w", "http_status": 403}
    else:
        up_data = {
            "name": name,
            "user_id": user_id
        }
        mdb_web.dbs["plug_invsys_type"].insert(up_data)
        data = {"msg": gettext("Add item type successfully"), "msg_type": "s", "http_status": 201}

    return data

def update_goods_types():

    '''
    添加商品分类
    :return:
    '''
    name = request.argget.all('name')
    id = request.argget.all('id')
    s, r = arg_verify([(gettext("name"), name), ("id", id)], required=True)
    if not s:
        return r
    user_id = current_user.str_id
    if mdb_web.dbs["plug_invsys_type"].find_one({"name":name, "user_id":user_id,
                                                 "_id":{"$ne":ObjectId(id)}}):
        data = {"msg": gettext("Item type already exists"), "msg_type": "w", "http_status": 403}
    else:
        mdb_web.dbs["plug_invsys_type"].update_one({"_id":ObjectId(id), "user_id":current_user.str_id},
                                                   {"$set":{"name":name}})
        data = {"msg": gettext("Update item type successfully"), "msg_type": "s", "http_status": 201}

    return data

def del_goods_types():

    '''
    删除商品分类
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
        if mdb_web.dbs["plug_invsys_category"].find_one({"type_id":id, "user_id":user_id}):
            faied_cnt += 1
            continue
        elif mdb_web.dbs["plug_invsys_business"].find_one({"type_id":id, "user_id":user_id}):
            faied_cnt += 1
            continue
        obj_ids.append(ObjectId(id))

    r = mdb_web.dbs["plug_invsys_type"].delete_many({"_id": {"$in": obj_ids}, "user_id":user_id})
    if r.deleted_count:
        data = {"msg": gettext("Successfully deleted {} type").format(r.deleted_count), "msg_type": "s",
                "http_status": 204}
    else:
        data = {"msg": gettext("Failed to delete"), "msg_type": "w", "http_status": 400}

    if faied_cnt:
        data["msg"] = gettext("There is {} type with a small category or a business, so you can't delete it.").format(faied_cnt)
    return data
