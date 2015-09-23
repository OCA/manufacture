# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields, models


class MrpConfigSettings(models.TransientModel):
    _inherit = 'mrp.config.settings'

    def _default_company_id(self):
        return self.env.user.company_id

    def _default_has_default_company(self):
        count = self.env['res.company'].search_count([])
        return bool(count == 1)

    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', required=True,
        default=_default_company_id)
    has_default_company = fields.Boolean(
        string='Has default company', readonly=True,
        default=_default_has_default_company)
    group_mrp_bom_version = fields.Boolean(
        string='Allow to re-edit BoMs',
        implied_group='mrp_bom_version.group_mrp_bom_version',
        help='The active state may be passed back to state draft')
    active_draft = fields.Boolean(
        string='Keep re-editing BoM active',
        help='This will allow you to define if those BoM passed back to draft'
        ' are still activated or not', related='company_id.active_draft')
