# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class WizCreateFictitiousOf(models.TransientModel):
    _name = "wiz.create.fictitious.of"

    date_planned = fields.Datetime(
        string='Scheduled Date', required=True, default=fields.Datetime.now)
    load_on_product = fields.Boolean("Load cost on product")
    project_id = fields.Many2one("project.project", string="Project")

    @api.multi
    def do_create_fictitious_of(self):
        production_obj = self.env['mrp.production']
        product_obj = self.env['product.product']
        routing_obj = self.env['mrp.routing']
        self.ensure_one()
        active_ids = self.env.context['active_ids']
        active_model = self.env.context['active_model']
        production_list = []
        if active_model == 'product.template':
            cond = [('product_tmpl_id', 'in', active_ids)]
            product_list = product_obj.search(cond)
        else:
            product_list = product_obj.browse(active_ids)
        for product in product_list:
            vals = {'product_id': product.id,
                    'product_template': product.product_tmpl_id.id,
                    'product_qty': 1,
                    'date_planned': self.date_planned,
                    'user_id': self._uid,
                    'active': False,
                    'product_uom': product.uom_id.id,
                    'project_id': self.project_id.id,
                    'analytic_account_id': (
                        self.project_id.analytic_account_id.id)
                    }
            prod_vals = production_obj.product_id_change(product.id,
                                                         1)['value']
            vals.update(prod_vals)
            if 'routing_id' in vals:
                routing = routing_obj.browse(vals['routing_id'])
                product_qty = production_obj._get_min_qty_for_production(
                    routing)
                vals['product_qty'] = product_qty
                prod_vals = production_obj.product_id_change(
                    product.id, product_qty)['value']
                vals.update(prod_vals)
            new_production = production_obj.create(vals)
            new_production.action_compute()
            new_production.calculate_production_estimated_cost()
            production_list.append(new_production.id)
        if self.load_on_product:
            for production_id in production_list:
                try:
                    production = production_obj.browse(production_id)
                    production.load_product_std_price()
                except:
                    continue
        return {'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'mrp.production',
                'type': 'ir.actions.act_window',
                'domain': "[('id','in'," + str(production_list) + "), "
                "('active','=',False)]"
                }
