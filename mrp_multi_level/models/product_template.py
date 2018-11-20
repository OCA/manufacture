# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    mrp_area_ids = fields.One2many(
        comodel_name='product.mrp.area',
        inverse_name='product_tmpl_id',
        string='MRP Area parameters',
    )
    mrp_area_count = fields.Integer(
        string='MRP Area Parameter Count',
        readonly=True,
        compute='_compute_mrp_area_count',
    )

    @api.multi
    def _compute_mrp_area_count(self):
        for rec in self:
            rec.mrp_area_count = len(rec.mrp_area_ids)

    @api.multi
    def action_view_mrp_area_parameters(self):
        self.ensure_one()
        action = self.env.ref('mrp_multi_level.product_mrp_area_action')
        result = action.read()[0]
        mrp_area_ids = self.with_context(
            active_test=False).mrp_area_ids.ids
        if len(mrp_area_ids) != 1:
            result['domain'] = [('id', 'in', mrp_area_ids)]
        else:
            res = self.env.ref('mrp_multi_level.product_mrp_area_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = mrp_area_ids[0]
        return result
