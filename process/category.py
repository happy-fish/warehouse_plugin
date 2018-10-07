# -*-coding:utf-8-*-
from flask import request
from flask_babel import gettext
from flask_login import current_user

from apps.app import mdb_web
from apps.utils.format.obj_format import objid_to_str

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

def get_categorys():

    '''
    获取一种商品的所有分类
    :return:
    '''
    goods_type_id = request.argget.all('goods_type_id')

    categorys = mdb_web.dbs["plug_invsys_category"].find({"type_id":goods_type_id,
                                                          "user_id":current_user.str_id})
    categorys = objid_to_str(categorys)
    data = {"categorys":categorys, "msg_type": "s", "msg":gettext("Successful data acquisition"),
            "http_status": 200}

    return data