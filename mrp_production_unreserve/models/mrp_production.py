# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp import workflow


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    unreserve_visible = fields.Boolean(
        string='MO Unreserve Visible',
        compute='_compute_unreserve_visible',
        help='Technical field to check when we can unreserve',
    )

    @api.depends('state', 'move_lines.reserved_quant_ids')
    def _compute_unreserve_visible(self):
        for order in self:
            if (order.state in ['done', 'cancel'] or not
                    order.move_lines.mapped('reserved_quant_ids')):
                order.unreserve_visible = False
            else:
                order.unreserve_visible = True

    @api.multi
    def button_unreserve(self):
        for production in self:
            production.move_lines.filtered(
                lambda x: x.state not in ('done', 'cancel')).do_unreserve()
            if not production.test_ready():
                workflow.trg_validate(
                    self.env.uid, 'mrp.production', production.id,
                    'moves_unreserved', self.env.cr)
        return True

    @api.multi
    def action_confirm(self):
        """If a MO comes from 'ready' state it doesn't need to be confirmed
        again."""
        from_draft = self.filtered(lambda mo: not mo.move_lines)
        res = super(MrpProduction, from_draft).action_confirm()
        self.write({'state': 'confirmed'})
        return res
