# -*- coding: utf-8 -*-
# (c) 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class QcInspection(models.Model):
    _inherit = 'qc.inspection'

    @api.depends('object_id')
    def get_production(self):
        for inspection in self:
            if inspection.object_id:
                if inspection.object_id._name == 'stock.move':
                    inspection.production = inspection.object_id.production_id
                elif inspection.object_id._name == 'mrp.production':
                    inspection.production = inspection.object_id

    @api.depends('object_id')
    def _get_product(self):
        """Overriden for getting the product from a manufacturing order."""
        for inspection in self:
            super(QcInspection, inspection)._get_product()
            if inspection.object_id and\
                    inspection.object_id._name == 'mrp.production':
                inspection.product = inspection.object_id.product_id

    production = fields.Many2one(
        comodel_name="mrp.production", compute="get_production", store=True)


class QcInspectionLine(models.Model):
    _inherit = 'qc.inspection.line'

    production = fields.Many2one(
        comodel_name="mrp.production", related="inspection_id.production",
        store=True, string="Production order")
