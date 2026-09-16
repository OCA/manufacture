# © 2026 FactorLibre - Adriana Saiz <adriana.saiz@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Create qc.trigger for pre-existing picking types that don't have one."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    existing_trigger_pt_ids = (
        env["qc.trigger"]
        .search([("picking_type_id", "!=", False)])
        .mapped("picking_type_id")
    )
    missing = (
        env["stock.picking.type"].with_context(active_test=False).search([])
        - existing_trigger_pt_ids
    )
    if missing:
        missing._create_qc_trigger()
