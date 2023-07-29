# Copyright 2019 Marcelo Frare (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# Copyright 2019 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MgmtsystemMgmInspection(models.Model):
    """
    Extends nonconformity adding related inspection
    """

    _inherit = ["mgmtsystem.nonconformity"]

    # new field
    # inspection reference
    inspection_id = fields.Many2one("qc.inspection", "Inspection")
