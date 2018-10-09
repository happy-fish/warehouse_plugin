# -*-coding:utf-8-*-
from bson import ObjectId
from flask import request
from flask_babel import gettext
from flask_login import current_user

from apps.app import mdb_web
from apps.core.flask.reqparse import arg_verify
from apps.utils.format.obj_format import objid_to_str, json_to_pyseq

__author__ = "Allen Woo"


def get_categorys():

    '''
    获取一种商品的所有分类
    :return:
    '''
    goods_type_id = request.argget.all('goods_type_id')
    categorys = mdb_web.dbs["plug_warehouse_category"].find({"type_id":goods_type_id,
                                                          "user_id":current_user.str_id})
    categorys = objid_to_str(categorys)
    data = {"categorys":categorys, "msg_type": "s", "msg":gettext("Successful data acquisition"),
            "http_status": 200}

    return data

def add_goods_categorys():

    '''
    添加商品分类
    :return:
    '''
    goods_type_id = request.argget.all('goods_type_id')
    name = request.argget.all('name')
    s, r = arg_verify([(gettext("name"), name), (gettext("goods_type_id"), goods_type_id)],
                      required=True)
    if not s:
        return r

    user_id = current_user.str_id
    if mdb_web.dbs["plug_warehouse_category"].find_one({"name":name, "type_id":goods_type_id,"user_id":user_id}):
        data = {"msg": gettext("Item category already exists"), "msg_type": "w", "http_status": 403}
    else:
        up_data = {
            "name": name,
            "type_id":goods_type_id,
            "user_id": user_id
        }
        mdb_web.dbs["plug_warehouse_category"].insert(up_data)
        data = {"msg": gettext("Add item category successfully"), "msg_type": "s", "http_status": 201}

    return data

def update_goods_categorys():

    '''
    添加商品分类
    :return:
    '''
    name = request.argget.all('name')
    goods_type_id = request.argget.all('goods_type_id')
    id = request.argget.all('id')
    s, r = arg_verify([(gettext("name"), name), ("id", id)], required=True)
    if not s:
        return r
    user_id = current_user.str_id
    if mdb_web.dbs["plug_warehouse_category"].find_one({"name":name, "user_id":user_id,"type_id":goods_type_id,
                                                 "_id":{"$ne":ObjectId(id)}}):
        data = {"msg": gettext("Item category already exists"), "msg_type": "w", "http_status": 403}
    else:
        mdb_web.dbs["plug_warehouse_category"].update_one({"_id":ObjectId(id), "user_id":current_user.str_id},
                                                   {"$set":{"name":name}})
        data = {"msg": gettext("Update item category successfully"), "msg_type": "s", "http_status": 201}

    return data

def del_goods_categorys():

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
        if mdb_web.dbs["plug_warehouse_goods"].find_one({"category_id":id, "user_id":user_id}):
            faied_cnt += 1
            continue
        obj_ids.append(ObjectId(id))

    r = mdb_web.dbs["plug_warehouse_category"].delete_many({"_id": {"$in": obj_ids}, "user_id":user_id})
    if r.deleted_count:
        data = {"msg": gettext("Successfully deleted {} category").format(r.deleted_count), "msg_type": "s",
                "http_status": 204}
    else:
        data = {"msg": gettext("Failed to delete"), "msg_type": "w", "http_status": 400}

    if faied_cnt:
        data["msg"] = gettext("There are {} category below the goods, can not be deleted, can not be deleted").format(faied_cnt)
    return data