# -*- coding: utf-8 -*-
# Copyright 2018 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)


class DictDiffer(object):
    """Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current = set(current_dict.keys())
        self.set_past = set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)

    def added(self):
        return self.set_current - self.intersect

    def removed(self):
        return self.set_past - self.intersect

    def changed(self):
        return set(o for o in self.intersect
                   if self.past_dict[o] != self.current_dict[o])

    def unchanged(self):
        return set(o for o in self.intersect
                   if self.past_dict[o] == self.current_dict[o])


class WizardMrpBomComparison(models.TransientModel):
    _name = 'wizard.mrp.bom.comparison'
    _description = "Compare two BoM"

    @api.model
    def _func_domain_bom_id(self):
        return self._domain_bom_id()

    @api.model
    def _domain_bom_id(self):
        """Returns the domain used to select the BoMs to compare."""
        bom_id = self.env.context.get('active_id', False)
        bom = self.env['mrp.bom'].browse(bom_id)
        return [('product_tmpl_id', '=', bom.product_tmpl_id.id)]

    @api.multi
    @api.depends('line_ids.diff_qty')
    def _compute_total_qty(self):
        for wiz in self:
            wiz.total_qty = sum([
                sum([line.diff_qty for line in wiz.line_changed_ids]),
                sum([line.diff_qty for line in wiz.line_added_ids]),
                sum([line.diff_qty for line in wiz.line_removed_ids]),
            ])

    bom1_id = fields.Many2one(
        'mrp.bom', u"BoM v1", required=True,
        domain=_func_domain_bom_id)
    bom2_id = fields.Many2one(
        'mrp.bom', u"BoM v2", required=True,
        domain=_func_domain_bom_id)
    line_ids = fields.One2many(
        'wizard.mrp.bom.comparison.line', 'wiz_id', u"Differences")
    line_changed_ids = fields.One2many(
        'wizard.mrp.bom.comparison.line', 'wiz_id', u"Products updated",
        domain=[('state', '=', 'changed')])
    line_added_ids = fields.One2many(
        'wizard.mrp.bom.comparison.line', 'wiz_id', u"Products added",
        domain=[('state', '=', 'added')])
    line_removed_ids = fields.One2many(
        'wizard.mrp.bom.comparison.line', 'wiz_id', u"Products removed",
        domain=[('state', '=', 'removed')])
    total_qty = fields.Float(
        u"Total qty",
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_compute_total_qty')

    @api.model
    def default_get(self, fields_list):
        """'default_get' method overridden."""
        res = super(WizardMrpBomComparison, self).default_get(fields_list)
        res['bom1_id'] = self.env.context.get('active_id', False)
        return res

    @api.model
    def _get_bom_line_data(self, root_bom, bom_line, factor=1):
        """Return a dictionary representation of the `bom_line` record.

        :return: a dictionary
        """
        data = {
            'product_id': bom_line.product_id.id,
            'product_code': bom_line.product_id.default_code or '-',
            'product_name': bom_line.product_id.name or '-',
            'bom_qty': (
                bom_line.product_qty / float(bom_line.bom_id.product_qty)
                * factor),
        }
        if bom_line.bom_id == root_bom:
            data['bom_qty'] = bom_line.product_qty * factor
        return data

    @api.model
    def _merge_bom_line_data(self, bom1_line_data, bom2_line_data):
        """Merge two bom lines (dictionaries with same keys).

        :return: a dictionary
        """
        new_bom_line_data = bom1_line_data.copy()
        new_bom_line_data['bom_qty'] += bom2_line_data['bom_qty']
        return new_bom_line_data

    @api.model
    def _get_all_data(self, root_bom):
        """Get all BoM data composing the BoM identified by `bom_id`.

        :return: a dictionary
        """
        products = {}

        def recurse(start_bom, products, factor=1):
            for bom_line in start_bom.bom_line_ids:
                if bom_line.product_id.bom_ids:
                    bom = self._get_bom_from_product(bom_line.product_id)
                    bom_factor = bom_line.product_qty * factor
                    recurse(bom, products, factor=bom_factor)
                if not bom_line.product_id:
                    continue
                p_id = bom_line.product_id.id
                bom_line_data = self._get_bom_line_data(
                    root_bom, bom_line, factor)
                # New product
                if p_id not in products:
                    products[p_id] = bom_line_data
                # Merge bom data with the existing one
                else:
                    products[p_id] = self._merge_bom_line_data(
                        products[p_id], bom_line_data)
            return products

        recurse(root_bom, products)
        return products

    def _get_bom_from_product(self, product):
        return product.bom_ids[0]

    @api.multi
    def run(self):
        """Make a comparison between two BoMs.

        :return: a report
        """
        self.ensure_one()
        # Ensure that no line exists if we make 2 comparisons
        # from the same wizard
        self.line_ids.unlink()
        _logger.info(
            u"BoM comparison between '%s' and '%s'...",
            self.bom1_id.product_tmpl_id.default_code,
            self.bom2_id.product_tmpl_id.default_code)
        comparison_line_model = self.env['wizard.mrp.bom.comparison.line']
        # Get all data for each BoM
        bom1_data = self._get_all_data(self.bom1_id)
        bom2_data = self._get_all_data(self.bom2_id)
        # Make the comparison between them
        diff = DictDiffer(bom2_data, bom1_data)
        # Iterate over data to generate lines to display on the report
        for p_id in diff.changed():
            v1 = bom1_data[p_id]
            v2 = bom2_data[p_id]
            vals = {
                'wiz_id': self.id,
                'product_id': p_id,
                'bom1_qty': v1['bom_qty'],
                'bom2_qty': v2['bom_qty'],
                'diff_qty': v2['bom_qty'] - v1['bom_qty'],
                'state': 'changed',
            }
            _logger.info(
                u"\tProduct updated: %s (ID=%s) %s -> %s",
                v1['product_code'], p_id,
                v1['bom_qty'], v2['bom_qty'])
            comparison_line_model.create(vals)
        for p_id in diff.added():
            v2 = bom2_data[p_id]
            vals = {
                'wiz_id': self.id,
                'product_id': p_id,
                'bom1_qty': 0.0,
                'bom2_qty': v2['bom_qty'],
                'diff_qty': v2['bom_qty'],
                'state': 'added',
            }
            _logger.info(
                u"\tProduct added: %s (ID=%s) -> %s",
                v2['product_code'], p_id, vals['diff_qty'])
            comparison_line_model.create(vals)
        for p_id in diff.removed():
            v1 = bom1_data[p_id]
            vals = {
                'wiz_id': self.id,
                'product_id': p_id,
                'bom1_qty': v1['bom_qty'],
                'bom2_qty': 0.0,
                'diff_qty': -v1['bom_qty'],
                'state': 'removed',
            }
            _logger.info(
                u"\tProduct removed: %s (ID=%s) -> %s",
                v1['product_code'], p_id, vals['diff_qty'])
            comparison_line_model.create(vals)
        _logger.info(
            u"BoM comparison between '%s' and '%s': printing report...",
            self.bom1_id.product_tmpl_id.default_code,
            self.bom2_id.product_tmpl_id.default_code)
        # Return the report
        return self.env['report'].get_action(
            self, 'mrp_bom_comparison.report_mrp_bom_comparison')


class WizardMrpBomComparisonLine(models.TransientModel):
    _name = 'wizard.mrp.bom.comparison.line'
    _description = "BoM line difference"

    wiz_id = fields.Many2one('wizard.mrp.bom.comparison', u"Wizard")
    product_id = fields.Many2one('product.product', u"Product")
    bom1_qty = fields.Float(
        u"v1-Qty", digits=dp.get_precision('Product Unit of Measure'))
    bom2_qty = fields.Float(
        u"v2-Qty", digits=dp.get_precision('Product Unit of Measure'))
    diff_qty = fields.Float(
        u"Qty gap", digits=dp.get_precision('Product Unit of Measure'))
    state = fields.Selection(
        [('changed', u"Changed"),
         ('added', u"Added"),
         ('removed', u"Removed"),
         ],
        u"State")
