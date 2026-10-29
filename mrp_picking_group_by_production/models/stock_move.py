# Copyright 2026 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _group_picking_by_production(self):
        """Moves that carry a production group without being chained to the
        production: components pulled with "Take From Stock, if unavailable,
        Trigger Another Rule" and the finished products pushed to stock.
        ``mrp`` only groups the transfers by production when the move feeds
        the raw material moves directly, so those end up mixed in a single
        transfer whenever the orders share a reference (e.g. the sale order
        that triggered them)."""
        self.ensure_one()
        return (
            bool(self.production_group_id) and not self._feeds_raw_material_production()
        )

    def _key_assign_picking(self):
        keys = super()._key_assign_picking()
        if self._group_picking_by_production():
            keys += (self.production_group_id,)
        return keys

    def _get_production_assignation_domain(self):
        domain = super()._get_production_assignation_domain()
        if not domain and self._group_picking_by_production():
            domain = [("production_group_id", "=", self.production_group_id.id)]
        return domain
