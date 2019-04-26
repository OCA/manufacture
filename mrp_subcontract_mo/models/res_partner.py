# Copyright 2019 Le Filament (<http://www.le-filament.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    # Boolean = Whether partner is a subcontractor
    subcontractor = fields.Boolean(string="Is a subcontractor")

    @api.model_create_multi
    def create(self, vals_list):
        # Overloads existing method from base module, with the following:
        # - Automatically creates subcontractor location is partner is a
        #     subcontractor

        # Returns:
        #     [partners] -- As per original create method
        partners = super(ResPartner, self).create(vals_list)
        for partner in partners:
            if partner.supplier and partner.subcontractor:
                # Create corresponding location
                self.env['stock.location'].create({
                    'location_id': self.env.ref(
                        "mrp_subcontract_mo.stock_location_subcontractor").id,
                    'name': partner.name,
                    'usage': 'internal',
                    'partner_id': partner.id,
                    })
        return partners
