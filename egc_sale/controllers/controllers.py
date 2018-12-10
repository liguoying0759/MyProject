# -*- coding: utf-8 -*-
from odoo import http

# class EgcSale(http.Controller):
#     @http.route('/egc_sale/egc_sale/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/egc_sale/egc_sale/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('egc_sale.listing', {
#             'root': '/egc_sale/egc_sale',
#             'objects': http.request.env['egc_sale.egc_sale'].search([]),
#         })

#     @http.route('/egc_sale/egc_sale/objects/<model("egc_sale.egc_sale"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('egc_sale.object', {
#             'object': obj
#         })