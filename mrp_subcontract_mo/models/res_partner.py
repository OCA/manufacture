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
        # - Automatically creates subcontractor location if partner is a
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

    @api.multi
    def write(self, vals):
        # Overloads existing method from base module, with the following:
        # - Automatically creates subcontractor location iF partner is a
        #     subcontractor and location does not already exist

        # Returns:
        #     [partners] -- As per original create method
        if vals.get('subcontractor') is True:
            for partner in self:
                # Check if corresponding location already exists
                subcos_location = self.env.ref(
                    "mrp_subcontract_mo.stock_location_subcontractor")
                # Retrieves selected subcontractor internal location
                if not self.env['stock.location'].search(
                        [('location_id', '=', subcos_location.id),
                         ('usage', '=', 'internal'),
                         ('partner_id', '=', partner.id)],
                        count=True) > 0:
                    # Create corresponding location
                    self.env['stock.location'].create({
                        'location_id': subcos_location.id,
                        'name': partner.name,
                        'usage': 'internal',
                        'partner_id': partner.id,
                        })
        return super(ResPartner, self).write(vals)
