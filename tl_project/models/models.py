# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TLProject(models.Model):
    _name = 'tl_project.project'

    name = fields.Char(string='工程名称')
    project_code = fields.Char(string='工程编码')
    client_code = fields.Char(string='客户编号')
    client_name = fields.Many2one('res.partner', string='客户名称')
    location = fields.Char(string='工程地址')
    construction_organization = fields.Char(string='施工单位')
    supervision_unit = fields.Char('监理单位')
    department_of_QA = fields.Char(string='质检部门')
    design_organization = fields.Char(string='设计单位')
    business_unit = fields.Char(string='业务单位')
    executing_state = fields.Boolean(string='执行状态', default=True)
    description = fields.Text(string='备注')










