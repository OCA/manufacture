# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class RepairLine(models.Model):

    _inherit = 'repair.line'

    order_state = fields.Selection(related='repair_id.state', store=True)

    @api.constrains('order_state','lot_id','product_id')
    def constrain_lot_id(self):
        return
