# Copyright 2016-19 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    mrp_production_auto_post_inventory = fields.Boolean(
        string="Production Auto Post-Inventory",
        help="Sets to automatic the post-inventory step in a manufacturing"
             "order. The inventory will be automatically posted after some "
             "quantity has been produced")
