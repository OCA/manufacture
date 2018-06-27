# -*- coding: utf-8 -*-
# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.multi
    @api.depends('qc_inspections', 'qc_inspections.state')
    def _count_inspections(self):
        self.ensure_one()
        self.created_inspections = len(self.qc_inspections)
        self.passed_inspections = len([x for x in self.qc_inspections if
                                       x.state == 'success'])
        self.failed_inspections = len([x for x in self.qc_inspections if
                                       x.state == 'failed'])
        self.done_inspections = (self.passed_inspections +
                                 self.failed_inspections)

    qc_inspections = fields.One2many(
        comodel_name='qc.inspection', inverse_name='lot', copy=False,
        string='Inspections', help="Inspections related to this lot.")
    created_inspections = fields.Integer(
        compute="_count_inspections", string="Created inspections")
    done_inspections = fields.Integer(
        compute="_count_inspections", string="Done inspections")
    passed_inspections = fields.Integer(
        compute="_count_inspections", string="Inspections OK")
    failed_inspections = fields.Integer(
        compute="_count_inspections", string="Inspections failed")
