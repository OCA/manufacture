# Copyright 2016 Antiun Ingenieria S.L. - Javier Iniesta
# Copyright 2019 Rubén Bravo <rubenred18@gmail.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
class MrpProduction(models.Model):
    _inherit = "mrp.production"

    source_procurement_group_id = fields.Many2one(
        comodel_name="procurement.group",
        readonly=True,
    )
    sale_org = fields.Many2one('sale.order')
    sale_id = fields.Many2one(
        "sale.order",
        string="Sale order",
        readonly=True,
        store=True,
        compute='_get_top_mrp_sale',
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="sale_id.partner_id",
        string="Customer",
        store=True,
    )
    commitment_date = fields.Datetime(
        related="sale_id.commitment_date", string="Commitment Date", store=True
    )
    client_order_ref = fields.Char(
        related="sale_id.client_order_ref", string="Customer Reference", store=True
    )

    @api.depends('procurement_group_id','mrp_production_source_count')
    @api.onchange('procurement_group_id','mrp_production_source_count')
    def _get_top_mrp_sale(self):
        for each in self:
            t = self._top_mo(each)
            if t:
               each.sale_id = t.source_procurement_group_id.sale_id or each.sale_org

    def _top_mo(self, mo):
        if mo.mrp_production_source_count == 0:
           return mo

        for each in mo.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.mrp_production_ids:
            return self._top_mo(each)
