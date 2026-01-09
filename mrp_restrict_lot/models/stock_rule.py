# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_mo_vals(
        self,
        product_id,
        product_qty,
        product_uom,
        location_dest_id,
        name,
        origin,
        company_id,
        values,
        bom,
    ):
        vals = super()._prepare_mo_vals(
            product_id,
            product_qty,
            product_uom,
            location_dest_id,
            name,
            origin,
            company_id,
            values,
            bom,
        )
        lot_id = values.get("restrict_lot_id")
        if lot_id:
            vals["lot_producing_id"] = lot_id
            lot = self.env["stock.lot"].browse(lot_id)
            mo_name = lot.name
            existing_mo = self.env["mrp.production"].search(
                [("lot_producing_id", "=", lot_id)]
            )
            if existing_mo:
                mo_name = f"{mo_name}-{len(existing_mo)}"
            vals["name"] = mo_name
        return vals

    def _make_mo_get_domain(self, procurement, bom):
        # (mrp). stock_rule._run_manufacture
        # calls _make_mo_get_domain then search for an MO
        # in order to increment its quantity
        # we don't want to mix MO with different lot_producing_id
        domain = super()._make_mo_get_domain(procurement, bom)
        restricted_lot = procurement.values.get("restrict_lot_id")
        if restricted_lot:
            # mind the last ,
            domain += (("lot_producing_id", "=", restricted_lot),)
        return domain
