# -*- coding: utf-8 -*-
# © 2014-2015 Avanzosc
# © 2014-2015 Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    @api.depends('analytic_line_ids', 'analytic_line_ids.amount',
                 'product_qty')
    def _compute_real_cost(self):
        for production in self:
            cost_lines = production.analytic_line_ids.filtered(
                lambda l: l.amount < 0)
            production.real_cost = -sum(cost_lines.mapped('amount'))
            production.unit_real_cost = (
                production.real_cost / production.product_qty)

    analytic_line_ids = fields.One2many(
        comodel_name="account.analytic.line", inverse_name="mrp_production_id",
        string="Cost Lines")
    real_cost = fields.Float(
        "Total Real Cost", compute="_compute_real_cost", store=True)
    unit_real_cost = fields.Float(
        "Unit Real Cost", compute="_compute_real_cost", store=True)

    @api.multi
    def action_production_end(self):
        res = super(MrpProduction, self).action_production_end()
        self.mapped('move_created_ids2').filtered(
            lambda l: l.state == 'done').product_price_update_production_done()
        return res

    @api.model
    def _prepare_real_cost_analytic_line(
            self, journal, name, production, product, general_account=None,
            workorder=None, qty=1, amount=0):
        """
        Prepare the vals for creating an analytic entry for real cost
        :param journal: Journal of the entry
        :param name: Name of the entry
        :param production: Origin product
        :param product: Product for the entry
        :param general_account: General account for the entry
        :param workorder: Origin workorder
        :param qty: Quantity for the entry. This quantity will multiply both
        standard and average costs for the entry costs.
        :param amount: Cost for calculating real cost.
        :return: Dictionary with the analytic entry vals.
        """
        analytic_line_obj = self.env['account.analytic.line']
        property_obj = self.env['ir.property']
        general_account = (
            general_account or product.property_account_expense or
            product.categ_id.property_account_expense_categ or
            property_obj.get('property_account_expense_categ',
                             'product.category'))
        return {
            'name': name,
            'mrp_production_id': production.id,
            'workorder': workorder and workorder.id or False,
            'account_id': self.analytic_account_id.id,
            'journal_id': journal.id,
            'user_id': self.env.uid,
            'date': analytic_line_obj._get_default_date(),
            'product_id': product and product.id or False,
            'unit_amount': qty,
            'amount': amount,
            'product_uom_id': product.uom_id.id,
            'general_account_id': general_account.id,
        }

    @api.multi
    def _costs_generate(self):
        """
        As we are generating the account_analytic_lines for MO in the
        current module, we override this method in order to avoid
        duplicates created in the parent class. Any other module
        inheriting this method should take this into account!
        """
        return
