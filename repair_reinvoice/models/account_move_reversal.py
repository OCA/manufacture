from odoo import models


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    def reverse_moves(self):
        action = super().reverse_moves()
        reversal_moves = self.new_move_ids
        for reversal_move in reversal_moves:
            reversed_move = reversal_move.reversed_entry_id
            if reversed_move.repair_ids:
                for repair in reversed_move.repair_ids:
                    repair.invoice_ids += reversal_move
        return action
