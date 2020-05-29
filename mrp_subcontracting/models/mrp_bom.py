# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
# Copyright 2019 Odoo
# Copyright 2020 Tecnativa - Alexandre Díaz
# Copyright 2020 Tecnativa - Pedro M. Baeza

from odoo import api, fields, models
from odoo.osv.expression import AND


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    type = fields.Selection(selection_add=[('subcontract', 'Subcontracting')])
    subcontractor_ids = fields.Many2many(
        'res.partner', 'mrp_bom_subcontractor', string='Subcontractors')

    def _bom_subcontract_find(self, product_tmpl=None, product=None,
                              picking_type=None, company_id=False,
                              bom_type='subcontract', subcontractor=False):
        domain = self._bom_find_domain(product_tmpl=product_tmpl,
                                       product=product,
                                       picking_type=picking_type,
                                       company_id=company_id,
                                       bom_type=bom_type)
        if subcontractor:
            domain = AND([domain, [
                ('subcontractor_ids', 'parent_of', subcontractor.ids),
            ]])
            return self.search(domain, order='sequence, product_id', limit=1)
        else:
            return self.env['mrp.bom']

    @api.model
    def _bom_find_domain(self, product_tmpl=None, product=None,
                         picking_type=None, company_id=False, bom_type=False):
        """Helper method that is present on v13 but not in v12. We recreate
        it here with v12 conditions.
        """
        if product:
            if not product_tmpl:
                product_tmpl = product.product_tmpl_id
            domain = [
                '|', ('product_id', '=', product.id),
                '&', ('product_id', '=', False),
                ('product_tmpl_id', '=', product_tmpl.id),
            ]
        elif product_tmpl:
            domain = [('product_tmpl_id', '=', product_tmpl.id)]
        if picking_type:
            domain += ['|', ('picking_type_id', '=', picking_type.id),
                       ('picking_type_id', '=', False)]
        if company_id or self.env.context.get('company_id'):
            domain = domain + [
                ('company_id', '=',
                 company_id or self.env.context.get('company_id'))]
        if bom_type:
            domain += [('type', '=', bom_type)]
        return domain
