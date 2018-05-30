# -*- coding: utf-8 -*-
from odoo import http

# class TlOptimize(http.Controller):
#     @http.route('/tl_sale_agreement/tl_sale_agreement/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tl_sale_agreement/tl_sale_agreement/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tl_sale_agreement.listing', {
#             'root': '/tl_sale_agreement/tl_sale_agreement',
#             'objects': http.request.env['tl_sale_agreement.tl_sale_agreement'].search([]),
#         })

#     @http.route('/tl_sale_agreement/tl_sale_agreement/objects/<model("tl_sale_agreement.tl_sale_agreement"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tl_sale_agreement.object', {
#             'object': obj
#         })