# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.one
    def _count_created_track_lot(self):
        return self.env['mrp.track.lot'].search_count([('production', '=',
                                                        self.id)])

    created_mrp_track_lot = fields.Integer(
        compute="_count_created_track_lot", string="Track Production Lots")

    @api.multi
    def action_view_track_lot_from_production(self):
        self.ensure_one()
        track_lot_obj = self.env['mrp.track.lot']
        idform = self.env.ref(
            'mrp_production_traceability.view_track_production_lot_form')
        idtree = self.env.ref(
            'mrp_production_traceability.view_track_production_lot_tree')
        search_view = self.env.ref('mrp_production_traceability.view_track_pro'
                                   'duction_lot_tree_filter')
        track_lots = track_lot_obj.search([('production', '=', self.id)])
        return {
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'mrp.track.lot',
            'views': [(idtree.id, 'tree'), (idform.id, 'form')],
            'search_view_id': search_view.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': "[('id','in',[" +
            ','.join(map(str, track_lots.ids)) + "])]",
            'context': self.env.context
            }
