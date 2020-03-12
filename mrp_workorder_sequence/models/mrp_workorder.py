# Copyright 2019-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MrpWorkOrder(models.Model):
    _inherit = "mrp.workorder"

    sequence = fields.Integer()
