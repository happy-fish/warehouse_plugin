# -*-coding:utf-8-*-
from flask import request

from apps.configs.sys_config import METHOD_WARNING
from apps.core.blueprint import api
from apps.core.flask.login_manager import osr_login_required
from apps.core.flask.response import response_format
from apps.plugins.warehouse_plugin.process.goods_category import add_goods_categorys, update_goods_categorys, \
    del_goods_categorys, get_categorys

__author__ = "Allen Woo"

@api.route('/plug/goods/category', methods=['GET','POST','PUT','DELETE'])
@osr_login_required
def api_plug_goods_category():

    '''
    GET:

    '''

    if request.c_method == "GET":
        data = get_categorys()
    elif request.c_method == "POST":
        data = add_goods_categorys()
    elif request.c_method == "PUT":
        data = update_goods_categorys()
    elif request.c_method == "DELETE":
        data = del_goods_categorys()
    else:
        data = {"msg_type":"w", "msg":METHOD_WARNING, "http_status":405}
    return response_format(data)