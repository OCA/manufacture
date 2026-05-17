from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.constrains("bom_id")
    def _check_component_attributes(self):
        self.bom_id._check_component_attributes()

    def _get_move_raw_values(
        self,
        product_id,
        product_uom_qty,
        product_uom,
        operation_id=False,
        bom_line=False,
    ):
        """Map a virtual ``bom.line`` (created in-memory by the dynamic
        component explosion) back to its persisted record before the FK is
        written to ``stock.move``. Without this, ``bom_line_id`` would be a
        ``NewId`` and the insert would fail.
        """
        values = super()._get_move_raw_values(
            product_id,
            product_uom_qty,
            product_uom,
            operation_id=operation_id,
            bom_line=bom_line,
        )
        if bom_line and not isinstance(bom_line.id, int):
            values["bom_line_id"] = bom_line._origin.id or False
        return values
