# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class QcTrigger(models.Model):
    _inherit = "qc.trigger"

    picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type", readonly=True, ondelete="cascade"
    )
