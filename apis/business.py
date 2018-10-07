# -*-coding:utf-8-*-
from flask import request

from apps.configs.sys_config import METHOD_WARNING
from apps.core.blueprint import api
from apps.core.flask.response import response_format
from apps.plugins.inventory_sys_plugin.process.business import get_businesses, add_business, update_business, del_business

__author__ = "Allen Woo"

@api.route('/plug/goods/business', methods=['GET','POST','PUT','DELETE'])
def api_plug_business():

    '''
    GET:

    '''

    if request.c_method == "GET":
        data = get_businesses()
    elif request.c_method == "POST":
        data = add_business()
    elif request.c_method == "PUT":
        data = update_business()
    elif request.c_method == "DELETE":
        data = del_business()
    else:
        data = {"msg_type":"w", "msg":METHOD_WARNING, "http_status":405}
    return response_format(data)