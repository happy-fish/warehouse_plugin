# -*-coding:utf-8-*-
from apps.plugins.inventory_sys_plugin.process.management import add_goods, update_goods, get_goods
from flask import request
from apps.core.flask.login_manager import osr_login_required
from apps.configs.sys_config import METHOD_WARNING
from apps.core.blueprint import api
from apps.core.flask.response import response_format
from apps.modules.post.process.post import get_post, get_posts, post_like

__author__ = 'Allen Woo'
@api.route('/plug/goods', methods=['GET','POST','PUT','DELETE'])
def api_plug_goods():

    '''
    GET:

    '''

    if request.c_method == "GET":
        get_goods()
    elif request.c_method == "POST":
        add_goods()
    elif request.c_method == "PUT":
        update_goods()
    else:
        data = {"msg_type":"w", "msg":METHOD_WARNING, "http_status":405}
    return response_format(data)