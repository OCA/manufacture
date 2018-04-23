# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    def use_case_action(self):
        for obj in self:
            products = self.env['product.product'].search([
                ('product_tmpl_id', '=', obj.id)
            ])
            for product in products:
                return product.use_case_action()


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def use_case_action(self):
        for obj in self:
            vals = {
                'product_id': obj.id
            }
            wizard = self.env['mrp.bom.component.find.wizard'].create(vals)
            return wizard.do_search_component()
