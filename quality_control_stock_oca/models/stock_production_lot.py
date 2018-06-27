# -*- coding: utf-8 -*-
# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.multi
    @api.depends('qc_inspections', 'qc_inspections.state')
    def _compute_count_inspections(self):
        for lot in self:
            lot.created_inspections = len(lot.qc_inspections)
            lot.passed_inspections = \
                len([x for x in lot.qc_inspections if x.state == 'success'])
            lot.failed_inspections = \
                len([x for x in lot.qc_inspections if x.state == 'failed'])
            lot.done_inspections = \
                (lot.passed_inspections + lot.failed_inspections)

    qc_inspections = fields.One2many(
        comodel_name='qc.inspection', inverse_name='lot', copy=False,
        string='Inspections', help="Inspections related to this lot.")
    created_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Created inspections")
    done_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Done inspections")
    passed_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Inspections OK")
    failed_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Inspections failed")
