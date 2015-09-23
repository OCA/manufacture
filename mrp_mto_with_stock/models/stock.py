# -*- encoding: utf-8 -*-
from openerp import fields, models, api
import pdb

class stock_move(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def action_confirm(self):
        '''Confirms stock move or put it in waiting if it's linked to another move.
        @returns list of ids'''
        res = super(stock_move, self).action_confirm()
        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

