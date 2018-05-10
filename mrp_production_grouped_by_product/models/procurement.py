# Copyright 2018 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProcuermentRule(models.Model):
    _inherit = 'procurement.rule'

    def _run_manufacture(self, product_id, product_qty, product_uom,
                         location_id, name, origin, values):
        bom = self._get_matching_bom(product_id, values)
        # Send to super for exception
        if not bom:
            return super(ProcuermentRule, self)._run_manufacture(
                product_id, product_qty, product_uom, location_id,
                name, origin, values)
        open_mo = self._find_equal_open_mo(
            product_id, bom, location_id, values)
        # Create mo as usual
        if not open_mo:
            return super(ProcuermentRule, self)._run_manufacture(
                product_id, product_qty, product_uom, location_id,
                name, origin, values)
        # Add product qty to mo
        self.env['change.production.qty'].create({
            'mo_id': open_mo.id,
            'product_qty': open_mo.product_qty + product_qty,
        }).change_prod_qty()
        # We pass the record in the context so the chatter is correctly written
        additional_context={'merge_products_into_mo': open_mo}
        return super(ProcuermentRule, self.with_context(**additional_context)
                     )._run_manufacture(product_id, product_qty, product_uom,
                                        location_id,name, origin, values)

    def _find_equal_open_mo(self, product_id, bom, location_id, values):
        """Returns the first occurrence according to conditions"""
        return self.env['mrp.production'].search([
            ('state', 'not in', ['progress', 'done', 'cancel']),
            ('product_id', '=', product_id.id),
            ('bom_id', '=', bom.id),
            ('location_dest_id', '=', location_id.id),
            ('company_id', '=', values.get('company_id').id),
        ], limit=1)
