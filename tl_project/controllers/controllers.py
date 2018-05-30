# -*- coding: utf-8 -*-
from odoo import http

# class Myproject(http.Controller):
#     @http.route('/tl_project/tl_project/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tl_project/tl_project/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tl_project.listing', {
#             'root': '/tl_project/tl_project',
#             'objects': http.request.env['tl_project.tl_project'].search([]),
#         })

#     @http.route('/tl_project/tl_project/objects/<model("tl_project.tl_project"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tl_project.object', {
#             'object': obj
#         })