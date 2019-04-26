# Copyright 2019 Le Filament (<http://www.le-filament.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MrpSubcontract(models.TransientModel):
    _name = "mrp.subcontract"
    _description = "Subcontract Production"

    @api.model
    def default_get(self, fields):
        # Retrieves default fields for the wizard and in particular:
        # - production_id = Manufacturing Order from where the wizard is called
        res = super(MrpSubcontract, self).default_get(fields)
        if self._context and self._context.get('active_id'):
            production = self.env['mrp.production'].browse(
                self._context['active_id'])
            if 'production_id' in fields:
                res['production_id'] = production.id
        return res

    # New fields:
    #    production_id       - Related Manufacturing Order (from where wizard
    #        is called)
    #    service_id          - Selected Service to be subcontracted
    #    subcontractor_id    - Selected Subcontractor
    production_id = fields.Many2one('mrp.production', 'Production')
    service_id = fields.Many2one(
        'product.product',
        domain=([('product_tmpl_id.type_subcontracting', '=', True)]),
        string='Service',
        help="Service linked to this operation")
    subcontractor_id = fields.Many2one(
        'res.partner',
        domain=([('subcontractor', '=', True)]),
        required=True,
        string='Subcontractor')

    @api.multi
    def do_subcontract(self):
        # Subcontracts the current Manufacturing Order to selected
        #    Subcontractor with purchasing of selected service (optional)

        # Make manufacturing order external (subcontracted)
        self.production_id.manufacturing_type = 'external'
        # Fills Manufacturing order subcontractor with selected one
        self.production_id.subcontractor_id = self.subcontractor_id
        # Fills Manufacturing order service with selected one
        self.production_id.service_id = self.service_id
        # Retrieves parent subcontractors location (defined in
        # data/location.xml)
        subcos_location = self.env.ref(
            "mrp_subcontract_mo.stock_location_subcontractor")
        # Retrieves selected subcontractor internal location
        subco_location = self.env['stock.location'].search(
            [('location_id', '=', subcos_location.id),
             ('usage', '=', 'internal'),
             ('partner_id', '=', self.production_id.subcontractor_id.id)],
            limit=1
            )
        # Assign Manufacturing Order raw and finished materials location to
        # subcontractor one
        self.production_id.location_dest_id = subco_location
        self.production_id.location_src_id = subco_location
        # In case Manufacturing Order is subcontracted we do not want to follow
        # routing instructions (since we do not want to generate Work Orders
        # for the subcontractor but only to subcontract the Manufacturing
        # Order)
        self.production_id.routing_id = False
        # Generates related delivery picking to send raw materials to subco
        self.production_id._generate_delivery_picking()
        # Generates related receipt picking to retrieve finished materials
        # from subco
        self.production_id._generate_return_picking()
        # If service is defined, generate related purchase order
        if self.production_id.service_id:
            self.production_id._generate_service_purchase()
