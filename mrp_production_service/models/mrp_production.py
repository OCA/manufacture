# Copyright 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.model
    def _prepare_service_procurement_values(self, production):
        location = production.location_src_id
        return {
            'company_id': production.company_id,
            'date_planned': production.date_planned_start,
            'warehouse_id': location.get_warehouse(),
            'group_id': production.procurement_group_id,
        }

    @api.model
    def _create_service_procurement(self, line):
        data = self._prepare_service_procurement(line)
        return self.env['procurement.rule'].create(data)

    @api.model
    def _action_launch_procurement_rule(self, line, production):
        values = self._prepare_service_procurement_values(production)

        name = '%s for %s' % (line.product_id.name,
                              production.name)
        self.env['procurement.group'].sudo().run(
            line.product_id, line.product_qty,
            line.product_uom_id,
            production.location_src_id, name,
            name, values)
        return True

    @api.multi
    def _generate_moves(self):
        res = super()._generate_moves()
        for production in self:
            factor = production.product_uom_id._compute_quantity(
                production.product_qty,
                production.bom_id.product_uom_id
            ) / production.bom_id.product_qty
            boms, lines = production.bom_id.explode(
                production.product_id, factor,
                picking_type=production.bom_id.picking_type_id)
            for line in lines:
                if line[0].product_id.type == 'service':
                    production._action_launch_procurement_rule(line[0],
                                                               production)
        return res
