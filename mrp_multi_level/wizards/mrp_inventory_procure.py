# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MrpInventoryProcure(models.TransientModel):
    _name = 'mrp.inventory.procure'
    _description = 'Make Procurements from MRP inventory projections'

    item_ids = fields.One2many(
        comodel_name='mrp.inventory.procure.item',
        inverse_name='wiz_id',
        string='Items',
    )

    @api.model
    def _prepare_item(self, mrp_inventory, qty_override=0.0):
        return {
            'qty': qty_override if qty_override else mrp_inventory.to_procure,
            'uom_id': mrp_inventory.uom_id.id,
            'date_planned': mrp_inventory.date,
            'mrp_inventory_id': mrp_inventory.id,
            'product_id': mrp_inventory.product_mrp_area_id.product_id.id,
            'warehouse_id': mrp_inventory.mrp_area_id.warehouse_id.id,
            'location_id': mrp_inventory.mrp_area_id.location_id.id,
        }

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        if self.user_has_groups(
                "mrp_multi_level.group_change_mrp_procure_qty"):
            view_id = self.env.ref(
                'mrp_multi_level.'
                'view_mrp_inventory_procure_wizard').id
        else:
            view_id = self.env.ref(
                'mrp_multi_level.'
                'view_mrp_inventory_procure_without_security').id
        return super(MrpInventoryProcure, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)

    @api.model
    def default_get(self, fields):
        res = super(MrpInventoryProcure, self).default_get(fields)
        mrp_inventory_obj = self.env['mrp.inventory']
        mrp_inventory_ids = self.env.context['active_ids'] or []
        active_model = self.env.context['active_model']
        if not mrp_inventory_ids or 'item_ids' not in fields:
            return res

        assert active_model == 'mrp.inventory', 'Bad context propagation'

        items = item_obj = self.env['mrp.inventory.procure.item']
        for line in mrp_inventory_obj.browse(mrp_inventory_ids):
            max_order = line.product_mrp_area_id.mrp_maximum_order_qty
            qty_to_order = line.to_procure
            if max_order and max_order < qty_to_order:
                # split the procurement in batches:
                while qty_to_order > 0.0:
                    qty = line.product_mrp_area_id._adjust_qty_to_order(
                        qty_to_order)
                    items += item_obj.create(self._prepare_item(line, qty))
                    qty_to_order -= qty
            else:
                items += item_obj.create(self._prepare_item(line))
        res['item_ids'] = [(6, 0, items.ids)]
        return res

    @api.multi
    def make_procurement(self):
        self.ensure_one()
        errors = []
        for item in self.item_ids:
            if not item.qty:
                raise ValidationError(_("Quantity must be positive."))
            values = item._prepare_procurement_values()
            # Run procurement
            try:
                self.env['procurement.group'].run(
                    item.product_id,
                    item.qty,
                    item.uom_id,
                    item.location_id,
                    'INT: ' + str(self.env.user.login),  # name?
                    'INT: ' + str(self.env.user.login),  # origin?
                    values
                )
                item.mrp_inventory_id.to_procure -= \
                    item.uom_id._compute_quantity(
                        item.qty, item.product_id.uom_id)
            except UserError as error:
                    errors.append(error.name)
            if errors:
                raise UserError('\n'.join(errors))
        return {'type': 'ir.actions.act_window_close'}


class MrpInventoryProcureItem(models.TransientModel):
    _name = 'mrp.inventory.procure.item'

    wiz_id = fields.Many2one(
        comodel_name='mrp.inventory.procure', string='Wizard',
        ondelete='cascade', readonly=True,
    )
    qty = fields.Float(string='Quantity')
    uom_id = fields.Many2one(
        string='Unit of Measure',
        comodel_name='product.uom',
    )
    date_planned = fields.Date(string='Planned Date', required=False)
    mrp_inventory_id = fields.Many2one(
        string='Mrp Inventory',
        comodel_name='mrp.inventory',
    )
    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
    )
    warehouse_id = fields.Many2one(
        string='Warehouse',
        comodel_name='stock.warehouse',
    )
    location_id = fields.Many2one(
        string='Location',
        comodel_name='stock.location',
    )

    def _prepare_procurement_values(self, group=False):
        return {
            'date_planned': fields.Datetime.to_string(
                fields.Date.from_string(self.date_planned)),
            'warehouse_id': self.warehouse_id,
            # 'company_id': self.company_id, # TODO: consider company
            'group_id': group,
        }

    @api.multi
    @api.onchange('uom_id')
    def onchange_uom_id(self):
        for rec in self:
            rec.qty = rec.mrp_inventory_id.uom_id._compute_quantity(
                rec.mrp_inventory_id.to_procure, rec.uom_id)
