# -*- coding: utf-8 -*-
# (c) 2014-2015 Avanzosc
# (c) 2014-2015 Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class WizCreateVirtualMo(models.TransientModel):
    _name = "wiz.create.virtual.mo"

    date_planned = fields.Datetime(
        string='Scheduled Date', required=True, default=fields.Datetime.now)
    load_on_product = fields.Boolean("Load cost on product")
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account", string="Analytic account")

    @api.multi
    def do_create_virtual_mo(self):
        self.ensure_one()
        production_obj = self.env['mrp.production']
        product_obj = self.env['product.product']
        routing_obj = self.env['mrp.routing']
        active_ids = self.env.context['active_ids']
        if self.env.context['active_model'] == 'product.template':
            cond = [('product_tmpl_id', 'in', active_ids)]
            products = product_obj.search(cond)
        else:
            products = product_obj.browse(active_ids)
        productions = self.env['mrp.production']
        for product in products:
            vals = {
                'product_id': product.id,
                'product_template': product.product_tmpl_id.id,
                'product_qty': 1,
                'date_planned': self.date_planned,
                'user_id': self._uid,
                'active': False,
                'product_uom': product.uom_id.id,
                'analytic_account_id': self.analytic_account_id.id,
            }
            vals.update(production_obj.product_id_change(
                product.id, 1)['value'])
            if 'routing_id' in vals:
                routing = routing_obj.browse(vals['routing_id'])
                product_qty = production_obj._get_min_qty_for_production(
                    routing) or 1
                vals['product_qty'] = product_qty
                prod_vals = production_obj.product_id_change(
                    product.id, product_qty)['value']
                vals.update(prod_vals)
            vals['product_attributes'] = [tuple([0, 0, line]) for line in
                                          vals.get('product_attributes', [])]
            new_production = production_obj.create(vals)
            new_production.action_compute()
            productions |= new_production
        if self.load_on_product:
            productions.load_product_std_price()
        return {
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'mrp.production',
            'type': 'ir.actions.act_window',
            'domain': ("[('id', 'in', %s), ('active','=',False)]" %
                       productions.ids)
        }
