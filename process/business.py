# -*-coding:utf-8-*-
from flask import request
from flask_babel import gettext
from flask_login import current_user

from apps.app import mdb_web
from apps.utils.format.obj_format import objid_to_str

__author__ = "Allen Woo"

def get_businesses():

    '''
    获取所有的厂商
    :return:
    '''
    goods_type_id = request.argget.all('goods_type_id')

    business = mdb_web.dbs["plug_invsys_business"].find({"type_id":goods_type_id, "user_id":current_user.str_id})
    business = objid_to_str(business)
    data = {"business":business, "msg_type": "s", "msg":gettext("Successful data acquisition"),
            "http_status": 200}

    return data