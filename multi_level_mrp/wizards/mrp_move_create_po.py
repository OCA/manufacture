# © 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# © 2016 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar <jordi.ballester@eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from datetime import date


class MrpMoveCreatePo(models.TransientModel):
    _name = 'mrp.move.create.po'

    move_id = fields.Many2one('mrp.move', 'Move', select=True)
    product_id = fields.Many2one('product.product', 'Product', select=True)
    main_supplier_id = fields.Many2one('res.partner', 'Main Supplier',
                                       select=True)
    partner_id = fields.Many2one('res.partner', 'Partner', select=True)
    mrp_qty = fields.Float('Quantity')
    mrp_date = fields.Date('Planned Date')
    qty_po = fields.Float('Quantity PO')
    date_po = fields.Date('Date PO')
    other_partner = fields.Boolean('Select Other Partner', default=False)
    purchase_line_warn = fields.Char('Purchase Warning')
    purchase_line_warn_msg = fields.Text('Purchase Warning')

    @api.multi
    def create_po(self):
        for move in self:
            if move.other_partner and move.partner_id:
                partner_selected = move.partner_id.id
                pricelist = move.partner_id.property_product_pricelist_purchase.id
                fiscalposition = move.partner_id.property_account_position.id
                currency_id = \
                    move.partner_id.property_product_pricelist_purchase.\
                    currency_id.id
            else:
                partner_selected = move.main_supplier_id.id
                pricelist = move.main_supplier_id.\
                    property_product_pricelist_purchase.id
                fiscalposition = \
                    move.main_supplier_id.property_account_position.id
                currency_id = move.main_supplier_id.\
                    property_product_pricelist_purchase.currency_id.id

            order_id = 0
            sql_stat = "SELECT id FROM purchase_order WHERE " \
                       "purchase_order.partner_id = %d AND state = 'draft' " \
                       "ORDER BY date_order DESC LIMIT 1" % \
                       (partner_selected, )
            self.env.cr.execute(sql_stat)
            sql_res = self.env.cr.dictfetchone()
            if sql_res:
                if sql_res['id']:
                    order_id = sql_res['id']

            unit_price = 0
            sql_stat = "SELECT price FROM product_supplierinfo, " \
                       "pricelist_partnerinfo WHERE " \
                       "product_supplierinfo.name =  %d AND product_tmpl_id " \
                       "= %d AND product_supplierinfo.id = suppinfo_id " \
                       "LIMIT 1" % (partner_selected,
                                    move.product_id.product_tmpl_id.id)
            self.env.cr.execute(sql_stat)
            sql_res = self.env.cr.dictfetchone()
            if sql_res:
                if sql_res['price']:
                    unit_price = sql_res['price']

            if order_id == 0:
                po = self.env['purchase.order']
                po_id = po.create({
                    'shipped': False,
                    'warehouse_id': 1,
                    'date_order': date.today(),
                    'location_id': 12,
                    'amount_untaxed': 0.00,
                    'partner_id': partner_selected,
                    'company_id': 1,
                    'amount_tax': 0.00,
                    'invoice_method': 'picking',
                    'state': 'draft',
                    'pricelist_id': pricelist,
                    'amount_total': 0.00,  
                    'journal_id': 2,
                    'accept_amount': False,
                    'fiscal_position': fiscalposition,
                    'currency_id': currency_id,
                })
                order_id = po_id

            if order_id != 0:
                pr = self.env['purchase.order.line']
                account_fiscal_position = \
                    self.env['account.fiscal.position']
                account_tax = self.env['account.tax']
                fpos = fiscalposition and account_fiscal_position.browse(
                    fiscalposition) or False
                taxes = account_tax.browse(map(lambda x: x.id,
                                 move.product_id.supplier_taxes_id))
                taxes_ids = account_fiscal_position.map_tax(fpos, taxes)
                pr_id = pr.create({
                    'product_id': move.product_id.id,
                    'product_uom': move.product_id.product_tmpl_id.uom_id.id,
                    'date_planned': move.date_po,
                    'order_id': order_id, 
                    'name': '[' + move.product_id.default_code + '] ' +
                            move.product_id.name,
                    'price_unit': unit_price,
                    'product_qty': move.qty_po,
                    'supplier_uom_id':
                        move.product_id.product_tmpl_id.uom_id.id,
                    'supplier_price_unit': unit_price,
                    'supplier_qty': move.qty_po,
                    'conversion_coeff': 1,
                    'taxes_id': [[6, False, taxes_ids]],
                    'description': False, 
                })

            order_number = None
            sql_stat = "SELECT name FROM purchase_order WHERE id = %d" % (
                order_id, )
            self.env.cr.execute(sql_stat)
            sql_res = self.env.cr.dictfetchone()
            if sql_res:
                if sql_res['name']:
                    order_number = sql_res['name']

            if 'move_id' in self.env.context and self.env.context['move_id']:
                move_obj = self.env['mrp.move']
                move_obj.write(self.env.context['move_id'], {
                    'purchase_order_id': order_id,
                    'purchase_order_line_id': pr_id,
                    'mrp_processed': True,
                    'current_qty': move.qty_po, 
                    'current_date': move.date_po, 
                    'name': order_number,
                })

        return True
