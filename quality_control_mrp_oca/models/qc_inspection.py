# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class QcInspection(models.Model):
    _inherit = 'qc.inspection'

    @api.one
    @api.depends('object_id')
    def get_production(self):
        self.production = False
        if self.object_id:
            if self.object_id._name == 'stock.move':
                self.production = self.object_id.production_id

    production = fields.Many2one(
        comodel_name="mrp.production", compute="get_production", store=True)


class QcInspectionLine(models.Model):
    _inherit = 'qc.inspection.line'

    production = fields.Many2one(
        comodel_name="mrp.production", related="inspection_id.production",
        store=True, string="Production order")
