# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EGCSale(models.Model):
    _inherit = 'sale.order'

    margin_percent = fields.Char(string='毛利百分比', compute='_product_margin', store=True)
    # client_order_ref = fields.Char(string='客户PO', copy=False,required=True)
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('approve', '审批'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    confirm_sample_time = fields.Datetime(string='确认样时间')
    component_sample_time = fields.Datetime(string='成分标样时间')
    test_sample_time = fields.Datetime(string='检测样时间')
    bulk_sample_time = fields.Datetime(string='大货样时间')
    confirm_sample_time_status = fields.Selection(
        [('sent','已寄'),
         ('confirmed','已确认')
         ],string='确认样状态'
    )
    component_sample_time_status = fields.Selection(
        [('sent', '已寄'),
         ('confirmed', '已确认')
         ],string='成分标状态'
    )
    test_sample_time_status = fields.Selection(
        [('sent', '已寄'),
         ('confirmed', '已确认')
         ], string='检测样状态'
    )
    bulk_sample_time_status = fields.Selection(
        [('sent', '已寄'),
         ('confirmed', '已确认')
         ],string='大货样状态'
    )

    @api.multi
    def confirm(self):
        # for order in self:
        if self.user_has_groups('sales_team.group_sale_manager'):
            return self.action_confirm()

        self.write({
            'state': 'approve',
            'confirmation_date': fields.Datetime.now()
        })

    @api.depends('order_line.margin')
    def _product_margin(self):
        for order in self:
            order.margin = sum(order.order_line.filtered(lambda r: r.state != 'cancel').mapped('margin'))
            if order.amount_total != 0:
                order.margin_percent = str(round((order.margin / order.amount_total) * 100, 2)) + '%'
