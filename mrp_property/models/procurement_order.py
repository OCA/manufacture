# coding: utf-8
# Copyright 2008 - 2016 Odoo S.A.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    property_ids = fields.Many2many(
        'mrp.property', 'procurement_property_rel',
        'procurement_id', 'property_id',
        string='Properties',
        help=("The BoM that has the same properties as this procurement will "
              "be selected unless there is a BoM with no properties at all."))

    @api.multi
    def _get_matching_bom(self):
        """ Inject property ids in the context, to be honoured in the
        production model's search method """
        return super(ProcurementOrder, self.with_context(
            property_ids=self.property_ids.ids))._get_matching_bom()
