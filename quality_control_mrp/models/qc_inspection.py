# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class QcInspection(models.Model):
    _inherit = 'qc.inspection'

    def _prepare_inspection_header(self, object_ref, trigger_line):
        res = super()._prepare_inspection_header(
            object_ref, trigger_line)
        # Fill qty when coming from pack operations
        if object_ref and object_ref._name == 'mrp.production':
            res['qty'] = object_ref.product_qty
        return res

    def object_selection_values(self):
        result = super().object_selection_values()
        result.append(('mrp.production', "Production"))
        return result

    @api.depends('object_id')
    def _compute_production(self):
        for inspection in self:
            if not inspection.object_id:
                continue
            obj_name = inspection.object_id._name
            if obj_name == 'stock.move':
                inspection.production = inspection.object_id.production_id
            elif obj_name == 'mrp.production':
                inspection.production = inspection.object_id

    @api.depends('object_id')
    def _compute_product_id(self):
        """Overriden for getting the product from a manufacturing order."""
        for inspection in self:
            super(QcInspection, inspection)._compute_product_id()
            if inspection.object_id and\
                    inspection.object_id._name == 'mrp.production':
                inspection.product_id = inspection.object_id.product_id

    production = fields.Many2one(
        comodel_name="mrp.production", compute="_compute_production",
        store=True)


class QcInspectionLine(models.Model):
    _inherit = 'qc.inspection.line'

    production = fields.Many2one(
        comodel_name="mrp.production", related="inspection_id.production",
        store=True, string="Production order")
