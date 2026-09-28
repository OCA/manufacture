# Copyright 2016 Antiun Ingenieria S.L. - Javier Iniesta
# Copyright 2019 Rubén Bravo <rubenred18@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    @api.depends('production_id.sale_id', 'production_id.partner_id',
                 'production_id.commitment_date', 'production_id.client_order_ref',
                 'production_id.sale_id.partner_id', 
                 'production_id.sale_id.commitment_date',
                 'production_id.sale_id.client_order_ref')
    def _compute_sale_info(self):
        """Compute sale information from manufacturing order.
        
        This method inherits sale information from the related manufacturing order.
        """
        for workorder in self:
            workorder.sale_id = workorder.production_id.sale_id
            workorder.partner_id = workorder.production_id.partner_id
            workorder.commitment_date = workorder.production_id.commitment_date
            workorder.client_order_ref = workorder.production_id.client_order_ref

    sale_id = fields.Many2one(
        comodel_name="sale.order",
        readonly=True, 
        store=True,
        compute='_compute_sale_info'
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        readonly=True, 
        store=True,
        compute='_compute_sale_info'
    )
    commitment_date = fields.Datetime(
        store=True,
        readonly=True,
        compute='_compute_sale_info'
    )
    client_order_ref = fields.Char(
        store=True,
        compute='_compute_sale_info'
    )