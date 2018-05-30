# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp

class TLSaleAgreement(models.Model):
    _name = 'tl_sale_agreement.sale_agreement'

    name = fields.Char(string='合同名称',required=True)
    description = fields.Text()
    client_name = fields.Many2one('res.partner', '客户名称')
    sale_agreement_lines = fields.One2many('tl_sale_agreement.sale_agreement_line','sale_agreement',string='合同行')
    contract_code = fields.Char(string='合同编号')
    # price = fields.Float(string='价格')
    project_address = fields.Many2one('tl_project.project',string='工程信息')
    start_time = fields.Date(string='开始时间')
    end_time = fields.Date(string='结束时间')
    estimated_amount = fields.Float(string='合计预估金额')
    issale = fields.Boolean('是否销售合同',default=True)
    # pay_type = fields.Many2one('account.payment.term', string='结算方式')
    haul_distance = fields.Char(string='运输距离')
    enable = fields.Boolean('是否有效',default=True)
    quotation_date = fields.Date(default=fields.Date.today, string='报价日期')
    contact = fields.Many2one('res.partner', string='联系人')
    salesman = fields.Many2one('res.partner', string='业务员')
    auditor = fields.Many2one('res.partner', string='审核人')
    audit_time = fields.Date(string='审核时间',default=fields.Datetime.now())
    amount_total = fields.Float(string='总计', store=True, readonly=True, compute='_amount_all')
    # agreement_type = fields.Many2one('tl_agreement.type',string='合同类型',required=True, default=_get_type_id)
    agreement_type = fields.Selection([('cash', '现金合同'), ('formal', '正式合同')],
                     'Type of agreement')


    state = fields.Selection([
        ('draft', '草稿'),
        ('confirmed', '确认'),
        ('done', '完成'),
    ], default='draft')

    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def action_confirm(self):
        self.state = 'confirmed'

    @api.multi
    def action_done(self):
        self.state = 'done'

    @api.depends('sale_agreement_lines.price_subtotal')
    def _amount_all(self):
        for order in self:
            amount_total = 0.0
            for line in order.sale_agreement_lines:
                amount_total += line.price_subtotal
            order.update({
                'amount_total': amount_total
            })

    # @api.onchange('agreement_type')
    # def onchange_agreement_type(self):
    #     if self.agreement_type.name=='现金合同':
    #            self.pay_type.id = 1

class TLSaleAgreementLine(models.Model):
    _name = 'tl_sale_agreement.sale_agreement_line'

    product_id = fields.Many2one('product.product',string='商品砼名称',domain=[('sale_ok','=',True)],required=True)
    number = fields.Integer(string='数量',digits=dp.get_precision('Product Unit of Measure'))
    qty_ordered = fields.Float(string='已订购数量')
    product_uom = fields.Char(string='单位')
    price_uint = fields.Float(string='单价')
    price_subtotal = fields.Float(string='小计')
    sale_agreement = fields.Many2one('tl_sale_agreement.sale_agreement', string='销售合同')
    # move_dest_id = fields.Many2one('stock.move','Downstream Move')
    schedule_date = fields.Date(string='预定交货日期')
    # account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    company_id = fields.Many2one('res.company', string='Company', store=True,
                                 readonly=True, default=lambda self: self.env['res.company']._company_default_get(
            'tl_sale_agreement.sale_agreement_line'))
    engineering_parts = fields.Char('浇筑部位')
    strength_grade = fields.Char(string='强度等级')
    unloading_method = fields.Char('卸料方式')
    impermeability_grade = fields.Char('抗渗等级')
    slump = fields.Char('坍落度')
    guaranteed_amount = fields.Char(string='保底方量')

    @api.onchange('number', 'price_uint')
    def _onchange_price(self):
        # set auto-changing field
        self.price_subtotal = self.number * self.price_uint

    @api.multi
    def _prepare_sale_order_line(self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False):
        self.ensure_one()
        sale_agreement = self.sale_agreement
        return {
            'name': name,
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_po_id.id,
            'product_uom_qty': product_qty,
            'price_unit': price_unit,
            'engineering_parts':self.engineering_parts,
            'unloading_method':self.unloading_method,
            'impermeability_grade':self.impermeability_grade,
            'slump':self.slump,
            'guaranteed_amount':self.guaranteed_amount,
            'strength_grade':self.strength_grade,
        }

    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id != self.product_uom):
            vals['product_uom'] = self.product_id.uom_id
            vals['number'] = 1.0

        self.strength_grade = self.product_id.strength_grade.name
        self.unloading_method = self.product_id.unloading_method.name
        self.impermeability_grade = self.product_id.impermeability_grade.name
        self.slump = self.product_id.slump.name
        self.product_uom = self.product_id.uom_id.name
        self.engineering_parts = self.product_id.engineering_parts.name

        product = self.product_id.with_context(
            lang=self.sale_agreement.client_name.lang,
            partner=self.sale_agreement.client_name.id,
            quantity=vals.get('number') or self.number,
        )

        result = {'domain': domain}

        title = False
        message = False
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False
                return result

        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name

        return result

    @api.multi
    def _get_display_price(self, product):
        # TO DO: move me in master/saas-16 on sale.order
        if self.sale_agreement.pricelist_id.discount_policy == 'with_discount':
            return product.with_context(pricelist=self.sale_agreement.pricelist_id.id).price
        final_price, rule_id = self.sale_agreement.pricelist_id.get_product_price_rule(self.product_id,
                                                                                 self.product_uom_qty or 1.0,
                                                                                 self.sale_agreement.partner_id)
        context_partner = dict(self.env.context, partner_id=self.sale_agreement.partner_id.id)
        base_price, currency_id = self.with_context(context_partner)._get_real_price_currency(self.product_id, rule_id,
                                                                                              self.product_uom_qty,
                                                                                              self.product_uom,
                                                                                              self.sale_agreement.pricelist_id.id)
        if currency_id != self.sale_agreement.pricelist_id.currency_id.id:
            base_price = self.env['res.currency'].browse(currency_id).with_context(context_partner).compute(base_price,
                                                                                                            self.sale_agreement.pricelist_id.currency_id)
        # negative discounts (= surcharge) are included in the display price
        return max(base_price, final_price)

class TLSaleOrder(models.Model):
    _inherit = 'sale.order'

    sales_agreement = fields.Many2one('tl_sale_agreement.sale_agreement', string='销售合同')
    agreement_type_code = fields.Selection([
        ('cash', '现金合同'),
        ('formal', '正式合同'),], related='sales_agreement.agreement_type',
        readonly=True)
    state1 = fields.Selection([
        ('draft','未收款'),
        ('confirm','已收款并确认任务单')
    ],default='draft')
    state2 = fields.Selection([
        ('draft','草稿'),
        ('confirm','已确认任务单')
    ],default='draft')

    @api.multi
    def confirm_receipt(self):
        self.state1 = 'confirm'
        self.action_confirm()

    @api.multi
    def confirm_task(self):
        self.state2 = 'confirm'
        self.action_confirm()

    @api.onchange('sales_agreement')
    def _onchange_requisition_id(self):
        if not self.sales_agreement:
            return
        # if self.sales_agreement:
        #     self.agreement_type_code = self.sales_agreement.agreement_type.code
        #     print("---------------"+self.agreement_type_code)

        sales_agreement = self.sales_agreement
        if self.partner_id:
            partner = self.partner_id
        else:
            partner = sales_agreement.client_name
        payment_term = partner.property_supplier_payment_term_id
        self.validity_date = sales_agreement.end_time
        self.partner_id = partner.id
        self.payment_term_id = payment_term.id,
        # self.currency_id = currency.id
        self.engineering_id = sales_agreement.project_address
        self.origin = sales_agreement.name
        self.partner_ref = sales_agreement.name
        # self.engineering_id = sales_agreement.project_address

        if len(sales_agreement.sale_agreement_lines)==1:
            order_lines = []
            for line in sales_agreement.sale_agreement_lines:
                product_lang = line.product_id.with_context({
                    'lang': partner.lang,
                    'partner_id': partner.id,
                })
                name = product_lang.display_name
                if product_lang.description_purchase:
                    name += '\n' + product_lang.description_purchase
                product_qty = line.number
                price_unit = line.price_uint
                order_line_values = line._prepare_sale_order_line(
                    name=name, product_qty=product_qty, price_unit=price_unit)
                # order_lines.append(order_line_values)
                order_lines.append((0, 0, order_line_values))
            self.order_line = order_lines
        # domain=[('self.order_line','=',sales_agreement.sale_agreement_lines)]
        # domain = {'order_line': [('product_id', 'in', sales_agreement.sale_agreement_lines.mapped('product_id')
                                  # )]}
        return {'domain':{'order_line':[('product_id','in',sales_agreement.sale_agreement_lines.mapped('product_id'))]}}

class TLSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    engineering_parts = fields.Char('浇筑部位')
    strength_grade = fields.Char(string='强度等级')
    unloading_method = fields.Char('卸料方式')
    impermeability_grade = fields.Char('抗渗等级')
    slump = fields.Char('坍落度')
    guaranteed_amount = fields.Char(string='保底方量')
    delivery_time = fields.Integer(string='供货开始时刻')
    supply_end_time = fields.Integer(string='供货结束时刻')
    number_of_mixer_truck = fields.Float(digits=(2,1),string='预估搅拌车数量')
    delivery_date = fields.Date(string='供货日期')
    receipt_number = fields.Integer(string='已签收方量')

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        return






