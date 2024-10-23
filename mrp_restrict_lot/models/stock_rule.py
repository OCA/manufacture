# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_mo_vals(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
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
            location_id,
            name,
            origin,
            company_id,
            values,
            bom,
        )
        lot_id = values.get("restrict_lot_id")
        if lot_id:
            vals["lot_producing_id"] = lot_id
            lot = self.env["stock.production.lot"].browse(lot_id)
            mo_name = lot.name
            existing_mo = self.env["mrp.production"].search(
                [("lot_producing_id", "=", lot_id)]
            )
            if existing_mo:
                mo_name = "%s-%s" % (mo_name, len(existing_mo))
            vals["name"] = mo_name
        return vals
