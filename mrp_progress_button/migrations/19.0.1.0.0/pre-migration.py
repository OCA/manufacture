# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.mrp_progress_button.hooks import fill_date_started


def migrate(cr, version):
    if not version:
        return
    fill_date_started(cr)
