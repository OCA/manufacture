# Copyright 2019 Marcelo Frare (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# Copyright 2019 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MgmtsystemMgmPartner(models.Model):
    """
    Extends partner with quality control triggers
    """

    _inherit = ["res.partner"]

    # new fields
    # trigger to activate inspection
    qc_triggers = fields.One2many(
        comodel_name="qc.trigger.partner_line",
        inverse_name="partner",
        string="Quality control triggers",
    )
