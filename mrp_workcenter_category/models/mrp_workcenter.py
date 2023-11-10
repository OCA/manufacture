# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    category_id = fields.Many2one(
        string="Category",
        comodel_name="mrp.workcenter.category",
    )
