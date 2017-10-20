# -*- coding: utf-8 -*-
# © 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm
from openerp import api, fields, models


class mrp_repair(orm.Model):
    """To inherit using old api is needed here in order to be able to modify
    the onchange method for `product_id`.
    NOTE: This should be moved to new api in v10, when the standard is also
    migrated.
    """
    _inherit = 'mrp.repair'

    def onchange_product_id(self, cr, uid, ids, product_id=None):
        res = super(mrp_repair, self).onchange_product_id(
            cr, uid, ids, product_id=product_id)
        product = self.pool['product.product'].browse(cr, uid, product_id)
        res['value']['to_refurbish'] = True if \
            product.refurbish_product_id else False
        return res


class MrpRepair(models.Model):
    _inherit = 'mrp.repair'

    to_refurbish = fields.Boolean('To refurbish')
    refurbish_location_dest_id = fields.Many2one(
        string='Refurbished Delivery Location', comodel_name='stock.location')
    refurbish_product_id = fields.Many2one(
        string='Refurbished product', comodel_name='product.product')
    refurbish_lot_id = fields.Many2one(
        string='Refurbished Lot', comodel_name='stock.production.lot')
    refurbish_move_id = fields.Many2one(
        string='Refurbished Inventory Move', comodel_name='stock.move')
    product_id = fields.Many2one(comodel_name='product.product')

    @api.onchange('to_refurbish', 'product_id')
    def _onchange_to_refurbish(self):
        if self.to_refurbish:
            self.refurbish_product_id = self.product_id.refurbish_product_id
            self.refurbish_location_dest_id = self.location_dest_id
            self.location_dest_id = self.product_id.property_stock_refurbish
        else:
            self.location_dest_id = self.refurbish_location_dest_id
            self.refurbish_product_id = False
            self.refurbish_location_dest_id = False

    @api.multi
    def action_repair_done(self):
        res = super(MrpRepair, self).action_repair_done()
        for repair in self:
            if repair.to_refurbish:
                move = self.env['stock.move'].create({
                    'name': repair.name,
                    'product_id': repair.refurbish_product_id.id,
                    'product_uom': repair.product_uom.id or
                    repair.refurbish_product_id.uom_id.id,
                    'product_uom_qty': repair.product_qty,
                    'partner_id': repair.address_id and
                    repair.address_id.id or False,
                    'location_id': repair.location_dest_id.id,
                    'location_dest_id': repair.refurbish_location_dest_id.id,
                    'restrict_lot_id': repair.refurbish_lot_id.id,
                })
                move.action_done()
                repair.refurbish_move_id = move.id
        return res


class mrp_repair_line(orm.Model):
    """To inherit using old api is needed here in order to be able to modify
    the onchange method for `type`.
    NOTE: This should be moved to new api in v10, when the standard is also
    migrated.
    """
    _inherit = 'mrp.repair.line'

    def onchange_operation_type(self, cr, uid, ids, type, guarantee_limit,
                                company_id=False, context=None):
        res = super(mrp_repair_line, self).onchange_operation_type(
            cr, uid, ids, type, guarantee_limit, company_id=company_id,
            context=context)

        if (type == 'add' and 'to_refurbish' in context and
                context['to_refurbish']):
            res['value']['location_dest_id'] = context[
                'refurbish_location_dest_id']
        elif (type == 'add' and 'to_refurbish' in context and not
                context['to_refurbish']):
            scrap_location_ids = self.pool['stock.location'].search(cr, uid, [
                ('usage', '=', 'customer')], context=context)
            res['value']['location_dest_id'] = scrap_location_ids[0]
        return res
