# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class MrpBomComponentFindWizard(models.TransientModel):
    _name = 'mrp.bom.component.find.wizard'

    product_id = fields.Many2one('product.product', 'Component', required=True)

    @api.multi
    def mrp_bom_component_find(self, wizard_id, component_id, level):
        cr = self._cr
        cr.execute("""
            select
                mbl.sequence,
                mbl.product_id,
                mbl.product_qty,
                mb.product_tmpl_id,
                mb.id mb_id,
                (select id from product_product
                 where product_tmpl_id=mb.product_tmpl_id limit 1) compose_id
            from mrp_bom_line mbl inner join mrp_bom mb on mbl.bom_id=mb.id
            where mbl.product_id=%s
        """, (str(component_id),))
        result = cr.fetchall()
        for row in result:
            compose_id = row[5]
            level_txt = ''
            for i in range(1, level):
                level_txt = level_txt + u'-'
            level_txt = level_txt + str(level)
            vals = {
                'wizard_id': wizard_id,
                'level': level_txt,
                'component_id': component_id,
                'line': row[0],
                'quantity': row[2],
                'mrp_bom_id': row[4],
            }
            self.env['mrp.bom.component.find.line'].create(vals)
            self.mrp_bom_component_find(wizard_id, compose_id, level + 1)

    @api.multi
    def do_search_component(self):
        for obj in self:
            if obj.product_id:
                self.mrp_bom_component_find(obj.id, obj.product_id.id, 1)
        return {
            'name': "Component find %s " % obj.product_id.name,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'mrp.bom.component.find.line',
            'type': 'ir.actions.act_window',
            'domain': [('wizard_id', '=', obj.id)],
        }


class MrpBomComponentFindLine(models.TransientModel):
    _name = 'mrp.bom.component.find.line'

    wizard_id = fields.Many2one('mrp.bom.component.find.wizard', 'Wizard')
    level = fields.Char('Level')
    component_id = fields.Many2one('product.product', 'Component')
    line = fields.Integer('Line')
    quantity = fields.Float(
        'Quantity', digits=dp.get_precision('Product Unit of Measure'))
    mrp_bom_id = fields.Many2one('mrp.bom', 'Product')
