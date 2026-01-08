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
    
    @api.depends('source_procurement_group_id', 'move_finished_ids.move_dest_ids.group_id',
                 'source_procurement_group_id.sale_id', 'source_procurement_group_id.sale_id.partner_id',
                 'source_procurement_group_id.sale_id.commitment_date', 'source_procurement_group_id.sale_id.client_order_ref',
                 'move_finished_ids.move_dest_ids.group_id.sale_id', 'move_finished_ids.move_dest_ids.group_id.sale_id.partner_id',
                 'move_finished_ids.move_dest_ids.group_id.sale_id.commitment_date', 'move_finished_ids.move_dest_ids.group_id.sale_id.client_order_ref')
    def _compute_sale_info(self):
        """Compute sale information for manufacturing orders.
        
        This method provides three strategies to find sale information:
        1. Use existing source_procurement_group_id
        2. Search through finished product move chain
        3. Search through raw material move chain
        """
        for production in self:
            # Strategy 1: Use existing source_procurement_group_id
            if production.source_procurement_group_id:
                procurement_group = production.source_procurement_group_id
            else:
                # Strategy 2: Search through finished product move chain
                procurement_group = production.move_finished_ids.move_dest_ids.group_id[:1]
                
                # Strategy 3: If not found, search through raw material move chain
                if not procurement_group:
                    procurement_group = production.move_raw_ids.group_id[:1]
            
            # Set sale information
            if procurement_group and procurement_group.sale_id:
                production.sale_id = procurement_group.sale_id
                production.partner_id = procurement_group.sale_id.partner_id
                production.commitment_date = procurement_group.sale_id.commitment_date
                production.client_order_ref = procurement_group.sale_id.client_order_ref
            else:
                # Clear all fields if no sale order is found
                production.sale_id = False
                production.partner_id = False
                production.commitment_date = False
                production.client_order_ref = False

    sale_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale order",
        readonly=True,
        store=True,
        compute='_compute_sale_info'
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        store=True,
        compute='_compute_sale_info'
    )
    commitment_date = fields.Datetime(
        string="Commitment Date",
        store=True,
        compute='_compute_sale_info'
    )
    client_order_ref = fields.Char(
        string="Customer Reference",
        store=True,
        compute='_compute_sale_info'
    )

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        """Extend search functionality to support customer reference search.
        
        Args:
            name (str): Search term
            args (list): Additional search domain
            operator (str): Search operator
            limit (int): Maximum number of results
            name_get_uid: User ID for name_get
            
        Returns:
            list: List of record IDs matching the search criteria
        """
        args = args or []
        domain = []
        
        if name:
            # Search by name or customer reference
            domain = ['|', ('name', operator, name), ('client_order_ref', operator, name)]
            
        return super(MrpProduction, self)._name_search(
            name, args + domain, operator=operator, limit=limit, name_get_uid=name_get_uid
        )