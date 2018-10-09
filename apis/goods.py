# -*-coding:utf-8-*-
from apps.plugins.inventory_sys_plugin.process.goods import add_goods, update_goods, get_goods, update_property, \
    update_cloth, get_more_goods
from flask import request
from apps.configs.sys_config import METHOD_WARNING
from apps.core.blueprint import api
from apps.core.flask.response import response_format

__author__ = 'Allen Woo'
@api.route('/plug/goods', methods=['GET','POST','PUT','DELETE'])
def api_plug_goods():

    '''
    GET:

    '''
    if request.c_method == "GET":
        if request.argget.all('goods_id'):
            data = get_goods()
        else:
            data = get_more_goods()

    elif request.c_method == "POST":
        data = add_goods()
    elif request.c_method == "PUT":
        if request.argget.all('update_property'):
            data = update_property()

        elif request.argget.all('update_cloth'):
            data = update_cloth()

        else:
            data = update_goods()
    else:
        data = {"msg_type":"w", "msg":METHOD_WARNING, "http_status":405}
    return response_format(data)