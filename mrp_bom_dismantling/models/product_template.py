# -*- coding: utf-8 -*-
# © 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    bom_count = fields.Integer(compute='_compute_bom_count')

    dismantling_bom_count = fields.Integer(
        compute='_compute_dismantling_bom_count'
    )

    @api.multi
    def _compute_bom_count(self):
        """ Override parent method to filter out dismantling bom.
        """
        if self.ids:
            counts = self._get_bom_count()

            for record in self:
                record.bom_count = counts[record.id]

    @api.multi
    def _compute_dismantling_bom_count(self):
        """ Compute the number of dismantling BoM for these templates.
        """
        if self.ids:
            counts = self._get_bom_count(dismantling=True)

            for record in self:
                record.dismantling_bom_count = counts[record.id]

    @api.multi
    def _get_bom_count(self, dismantling=False):
        templates_bom = {
            template_id: 0
            for template_id in self.ids
        }

        if dismantling:
            template_field = 'dismantled_product_tmpl_id'
        else:
            template_field = 'product_tmpl_id'

        boms = self.env['mrp.bom'].search([
            (template_field, 'in', self.ids),
            ('dismantling', '=', dismantling),
        ])
        for bom in boms:
            templates_bom[bom[template_field].id] += 1

        return templates_bom

    @api.multi
    def action_view_dismantling_bom(self):
        """ Return the dismantling BOM tree view act window which is filtered
        for these templates.
        """

        self.ensure_one()

        action = self.env['ir.actions.act_window'].for_xml_id(
            'mrp_bom_dismantling', 'mrp_bom_dismantling_form_action'
        )

        action['domain'] = [
            ('dismantling', '=', True),
            ('dismantled_product_tmpl_id', '=', self.id),
        ]
        action['context'] = {'is_dismantling': True}

        return action
