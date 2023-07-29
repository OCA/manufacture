# Copyright 2019 Marcelo Frare (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# Copyright 2019 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class QcProduct(models.Model):
    """
    Extends product model with a field to store quality control plan assigned
    """

    _inherit = ["qc.trigger.product_template_line"]

    # new filed
    # product's control plan
    plan_id = fields.Many2one("qc.plan", "Plan")


class QcCategory(models.Model):
    """
    Extends product category model with a field to store quality control plan assigned
    """

    _inherit = ["qc.trigger.product_category_line"]

    # new filed
    # sets product category's control plan
    plan_id = fields.Many2one("qc.plan", "Plan")
