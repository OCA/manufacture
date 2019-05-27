# -*- coding: utf-8 -*-
# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    # re-defines the field to change the default
    sequence = fields.Integer(default=9999)

    # displays sequence on the stock moves
    sequence2 = fields.Integer(help="Shows the sequence in the BOM line.",
                               related='sequence', readonly=False, store=True)

    @api.model
    def create(self, values):
        move = super(MrpBomLine, self).create(values)
        # We do not reset the sequence if we are copying a complete bom
        if not self.env.context.get('keep_line_sequence', False):
            move.bom_id._reset_sequence()
        return move


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.multi
    @api.depends('bom_line_ids')
    def _compute_max_line_sequence(self):
        """Allow to know the highest sequence entered in move lines.
        Then we add 1 to this value for the next sequence, this value is
        passed to the context of the o2m field in the view.
        So when we create new move line, the sequence is automatically
        incremented by 1. (max_sequence + 1)
        """
        for bom in self:
            bom.max_line_sequence = (
                max(bom.mapped('bom_line_ids.sequence') or [0]) + 1
                )

    max_line_sequence = fields.Integer(string='Max sequence in lines',
                                       compute='_compute_max_line_sequence')

    @api.multi
    def _reset_sequence(self):
        for rec in self:
            current_sequence = 1
            for line in rec.bom_line_ids:
                line.sequence = current_sequence
                current_sequence += 1

    @api.multi
    def copy(self, default=None):
        return super(MrpBom,
                     self.with_context(keep_line_sequence=True)).copy(default)
