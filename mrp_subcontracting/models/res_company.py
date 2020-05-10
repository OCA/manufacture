# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
# Copyright 2019 Odoo
# Copyright 2020 Tecnativa - Alexandre Díaz
# Copyright 2020 Tecnativa - Pedro M. Baeza

from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    subcontracting_location_id = fields.Many2one('stock.location')

    @api.model
    def create_missing_subcontracting_location(self):
        company_without_subcontracting_loc = self.env['res.company'].search(
            [('subcontracting_location_id', '=', False)])
        company_without_subcontracting_loc._create_subcontracting_location()

    def create_transit_location(self):
        """As there's no standard method for creating locations and we must
        create the subcontracting location before the warehouse creation, we
        inherit this method for performing the subcontracting location
        creation as well.
        """
        res = super().create_transit_location()
        self._create_subcontracting_location()
        return res

    def _create_subcontracting_location(self):
        parent_location = self.env.ref(
            'stock.stock_location_locations_partner', raise_if_not_found=False)
        property_stock_subcontractor_res_partner_field = self.env[
            'ir.model.fields'].search([
                ('model', '=', 'res.partner'),
                ('name', '=', 'property_stock_subcontractor')
            ])
        for company in self:
            subcontracting_location = self.env['stock.location'].create({
                'name': _('%s: Subcontracting Location') % company.name,
                'usage': 'internal',
                'location_id': parent_location.id,
                'company_id': company.id,
            })
            self.env['ir.property'].create({
                'name': 'property_stock_subcontractor_%s' % company.name,
                'fields_id': property_stock_subcontractor_res_partner_field.id,
                'company_id': company.id,
                'value': 'stock.location,%d' % subcontracting_location.id,
            })
            company.subcontracting_location_id = subcontracting_location
