from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = "mrp.production"
    
    mrp_group_ids = fields.Many2many('mrp.group',string='MRP Groups')
    
    @api.onchange('bom_id')
    def _onchange_bom(self):
        for rec in self:
            if rec.bom_id:
                rec.mrp_group_ids=rec.bom_id.mrp_group_ids