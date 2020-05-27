# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_cancel(self):
        orig_moves = self.mapped('move_orig_ids')
        productions = orig_moves.mapped('production_id')
        if productions and all(
            production.state == 'confirmed' for production in productions
        ):
            res = super(StockMove, self.with_context(
                bypass_check_state=True))._action_cancel()
            finish_moves = productions.mapped('move_finished_ids').filtered(
                lambda x: x.state not in ('done', 'cancel'))
            raw_moves = productions.mapped('move_raw_ids').filtered(
                lambda x: x.state not in ('done', 'cancel'))
            if all(x not in self for x in (finish_moves | raw_moves)):
                for production in productions:
                    production.action_cancel()
            return res
        return super()._action_cancel()
