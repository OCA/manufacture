# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _should_auto_confirm_procurement_mo(self, p):
        if (
            p.move_dest_ids.raw_material_production_id
            and p.company_id.mrp_procurement_no_autoconfirm
        ):
            return False
        return super()._should_auto_confirm_procurement_mo(p)
