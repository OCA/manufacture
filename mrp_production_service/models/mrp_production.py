# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.model
    def _prepare_service_procurement(self, line, production):
        location = production.location_src_id
        return {
            'name': '%s for %s' % (line.product_id.name, production.name),
            'origin': production.origin,
            'company_id': production.company_id.id,
            'date_planned_start': production.date_planned_start,
            'product_id': line.product_id.id,
            'product_qty': line.product_qty,
            'product_uom': line.product_uom_id.id,
            'location_id': location.id,
            'warehouse_id': location.get_warehouse().id
        }

    @api.model
    def _create_service_procurement(self, line, production):
        data = self._prepare_service_procurement(line, production)
        return self.env['procurement.order'].create(data)

    @api.multi
    def _generate_moves(self):
        res = super(MrpProduction, self)._generate_moves()
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
                    self._create_service_procurement(line[0], production)
        return res
