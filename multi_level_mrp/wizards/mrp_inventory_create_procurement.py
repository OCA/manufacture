# © 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# © 2016 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar <jordi.ballester@eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _


class MrpInventoryCreateProcurement(models.TransientModel):
    _name = 'mrp.inventory.create.procurement'

    @api.model
    def default_get(self, fields):
        res = super(MrpInventoryCreateProcurement, self).default_get(
            fields)
        mrp_inventory_ids = self.env.context['active_ids'] or []
        active_model = self.env.context['active_model']

        if not mrp_inventory_ids:
            return res
        assert active_model == 'mrp.inventory', \
            'Bad context propagation'
        return res

    @api.model
    def _prepare_procurement_from_mrp_inventory(self, mrp_inventory):
        user = self.env['res.users'].browse(self.env.uid).login
        mrp_area = mrp_inventory.mrp_area_id or False
        warehouse = mrp_area and mrp_area.warehouse_id or False
        product = mrp_inventory.mrp_product_id and \
            mrp_inventory.mrp_product_id.product_id or False

        return {
            'name': 'INT: '+str(user),
            'company_id': warehouse.company_id and
            warehouse.company_id.id or False,
            'date_planned': mrp_inventory.date,
            'product_id': product and product.id or False,
            'product_qty': mrp_inventory.to_order,
            'product_uom': product and
            product.uom_id and product.uom_id.id or False,
            'location_id': mrp_area.location_id and
            mrp_area.location_id.id or False,
            'warehouse_id': warehouse and warehouse.id or False
        }

    @api.multi
    def make_procurement_order(self):
        res = []
        procurement_obj = self.env['procurement.order']
        mrp_inventory_obj = self.env['mrp.inventory']
        mrp_inventory_ids = self.env.context['active_ids']

        for mrp_inventory in mrp_inventory_obj.browse(mrp_inventory_ids):
            procurement_data = self._prepare_procurement_from_mrp_inventory(
                mrp_inventory)
            procurement = procurement_obj.create(procurement_data)
            res.append(procurement.id)

        return {
            'domain': "[('id','in', ["+','.join(map(str, res))+"])]",
            'name': _('Procurement Order'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'procurement.order',
            'view_id': False,
            'context': False,
            'type': 'ir.actions.act_window'
        }
