# © 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# © 2016 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar <jordi.ballester@eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _
from datetime import date, datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class MultiLevelMrp(models.TransientModel):
    _name = 'multi.level.mrp'

    @api.model
    def _prepare_mrp_product_data(self, product, mrp_area):
        main_supplier_id = False
        sequence = 9999
        # TODO: All this should not be really needed, as at the time
        # of procurement you will figure out these details.
        for supplier in product.product_tmpl_id.seller_ids:
            if supplier.sequence < sequence:
                sequence = supplier.sequence
                main_supplier_id = supplier.name.id
        supply_method = 'produce'
        for route in product.product_tmpl_id.route_ids:
            if route.name == 'Buy':
                supply_method = 'buy'
        qty_available = 0.0
        product_obj = self.env['product.product']
        location_ids = self.env['stock.location'].search(
            [('id', 'child_of', mrp_area.location_id.id)])
        for location in location_ids:
            product_l = product_obj.with_context(
                {'location': location.id}).browse(product.id)
            qty_available += product_l.qty_available

        return {
            'mrp_area_id': mrp_area.id,
            'product_id': product.id,
            'mrp_qty_available': product.qty_available,
            'mrp_llc': product.llc,
            'nbr_mrp_actions': 0,
            'nbr_mrp_actions_4w': 0,
            'name': product.name,
            'supply_method': supply_method,
            'main_supplier_id': main_supplier_id,
            }

    @api.model
    def _prepare_mrp_move_data_from_forecast(self, fc, fc_id, mrpproduct):
        mrp_type = 'd'
        origin = 'fc'
        mrp_date = date.today()
        if datetime.date(datetime.strptime(fc_id.date,
                                           '%Y-%m-%d')) > date.today():
            mrp_date = datetime.date(datetime.strptime(
                fc_id.date, '%Y-%m-%d'))
        return {
            'mrp_area_id': fc.mrp_area_id.id,
            'product_id': fc.product_id.id,
            'mrp_product_id': mrpproduct.id,
            'production_id': None,
            'purchase_order_id': None,
            'purchase_line_id': None,
            'sale_order_id': None,
            'sale_line_id': None,
            'stock_move_id': None,
            'mrp_qty': -fc_id.qty_forecast,
            'current_qty': -fc_id.qty_forecast,
            'mrp_date': mrp_date,
            'current_date': mrp_date,
            'mrp_action': 'none',
            'mrp_type': mrp_type,
            'mrp_processed': False,
            'mrp_origin': origin,
            'mrp_order_number': None,
            'parent_product_id': None,
            'running_availability': 0.00,
            'name': 'Forecast',
            'state': 'confirmed',
        }

    @api.model
    def _prepare_mrp_move_data_from_stock_move(self, mrp_product, move):
        # TODO: Clean up to reduce dependencies
        if (move.location_id.usage == 'internal' and
                move.location_dest_id.usage != 'internal') \
                or (move.location_id.usage != 'internal' and
                            move.location_dest_id.usage == 'internal'):
            if move.location_id.usage == 'internal':
                mrp_type = 'd'
                productqty = -move.product_qty
            else:
                mrp_type = 's'
                productqty = move.product_qty
            po = None
            po_line = None
            so = None
            so_line = None
            mo = None
            origin = None
            order_number = None
            parent_product_id = None
            if move.purchase_line_id:
                order_number = move.purchase_line_id.order_id.name
                origin = 'po'
                po = move.purchase_line_id.order_id.id
                po_line = move.purchase_line_id.id
            if move.production_id:
                order_number = move.production_id.name
                origin = 'mo'
                mo = move.production_id.id
            else:
                # TODO: move.move_dest_id -> move.move_dest_ids
                if move.move_dest_ids:
                    move_dest_id = move.move_dest_ids[0]
                    if move.move_dest_id.production_id:
                        order_number = \
                            move_dest_id.production_id.name
                        origin = 'mo'
                        mo = move_dest_id.production_id.id
                        if move_dest_id.production_id.product_id:
                            parent_product_id = \
                                move_dest_id.production_id.product_id.id
                        else:
                            parent_product_id = \
                                move_dest_id.product_id.id
            if order_number is None:
                order_number = move.name
            mrp_date = date.today()
            if datetime.date(datetime.strptime(
                    move.date, '%Y-%m-%d %H:%M:%S')) > date.today():
                mrp_date = datetime.date(datetime.strptime(
                    move.date, '%Y-%m-%d %H:%M:%S'))
            return {
                'mrp_area_id': mrp_product.mrp_area_id.id,
                'product_id': move.product_id.id,
                'mrp_product_id': mrp_product.id,
                'production_id': mo,
                'purchase_order_id': po,
                'purchase_line_id': po_line,
                'sale_order_id': so,
                'sale_line_id': so_line,
                'stock_move_id': move.id,
                'mrp_qty': productqty,
                'current_qty': productqty,
                'mrp_date': mrp_date,
                'current_date': move.date,
                'mrp_action': 'none',
                'mrp_type': mrp_type,
                'mrp_processed': False,
                'mrp_origin': origin,
                'mrp_order_number': order_number,
                'parent_product_id': parent_product_id,
                'running_availability': 0.00,
                'name': order_number,
                'state': move.state,
            }
        return {}

    @api.model
    def _prepare_mrp_move_data_supply(self, product, qty, mrp_date_supply,
                                      mrp_action_date, mrp_action, name):
        return {
                    'mrp_area_id': product.mrp_area_id.id,
                    'product_id': product.product_id.id,
                    'mrp_product_id': product.id,
                    'production_id': None,
                    'purchase_order_id': None,
                    'purchase_line_id': None,
                    'sale_order_id': None,
                    'sale_line_id': None,
                    'stock_move_id': None,
                    'mrp_qty': qty,
                    'current_qty': None,
                    'mrp_date': mrp_date_supply,
                    'mrp_action_date': mrp_action_date,
                    'current_date': None,
                    'mrp_action': mrp_action,
                    'mrp_type': 's',
                    'mrp_processed': False,
                    'mrp_origin': None,
                    'mrp_order_number': None,
                    'parent_product_id': None,
                    'name': 'Supply: ' + name,
                }

    @api.model
    def _prepare_mrp_move_data_bom_explosion(self, product, bomline, qty,
                                             mrp_date_demand_2, bom, name):
            mrp_products = self.env['mrp.product'].search(
                [('mrp_area_id', '=', product.mrp_area_id.id),
                 ('product_id', '=', bomline.product_id.id)], limit=1)
            if not mrp_products:
                raise exceptions.Warning(
                    _("No MRP product found"))

            return {
                'mrp_area_id': product.mrp_area_id.id,
                'product_id': bomline.product_id.id,
                'mrp_product_id': mrp_products[0].id,
                'production_id': None,
                'purchase_order_id': None,
                'purchase_line_id': None,
                'sale_order_id': None,
                'sale_line_id': None,
                'stock_move_id': None,
                'mrp_qty': -(qty * bomline.product_qty),
                'current_qty': None,
                'mrp_date': mrp_date_demand_2,
                'current_date': None,
                'mrp_action': 'none',
                'mrp_type': 'd',
                'mrp_processed': False,
                'mrp_origin': 'mrp',
                'mrp_order_number': None,
                'parent_product_id': bom.product_id.id,
                'name':
                    ('Demand Bom Explosion: ' + name).replace(
                        'Demand Bom Explosion: Demand Bom '
                        'Explosion: ',
                        'Demand Bom Explosion: '),
            }

    @api.model
    def create_move(self, mrp_product_id, mrp_date, mrp_qty, name):
        self = self.with_context(auditlog_disabled=True)

        values = {}
        if not isinstance(mrp_date, date):
            mrp_date = datetime.date(datetime.strptime(mrp_date, '%Y-%m-%d'))

        qty_ordered = 0.00
        products = self.env['mrp.product'].search([('id', '=',
                                                    mrp_product_id)])
        for product in products:
            if product.supply_method == 'buy':
                # if product.purchase_requisition:
                #     mrp_action = 'pr'
                # else:
                mrp_action = 'po'
            else:
                mrp_action = 'mo'

            if mrp_date < date.today():
                mrp_date_supply = date.today()
            else:
                mrp_date_supply = mrp_date

            mrp_action_date = mrp_date-timedelta(days=product.mrp_lead_time)

            qty_ordered = 0.00
            qty_to_order = mrp_qty
            while qty_ordered < mrp_qty:
                qty = 0.00
                if product.mrp_maximum_order_qty == 0.00 and \
                                product.mrp_minimum_order_qty == 0.00:
                    qty = qty_to_order
                else:
                    if qty_to_order < product.mrp_minimum_order_qty:
                        qty = product.mrp_minimum_order_qty
                    else:
                        if product.mrp_maximum_order_qty and qty_to_order > \
                                product.mrp_maximum_order_qty:
                            qty = product.mrp_maximum_order_qty
                        else:
                            qty = qty_to_order
                qty_to_order -= qty

                move_data = self._prepare_mrp_move_data_supply(product, qty,
                                                               mrp_date_supply,
                                                               mrp_action_date,
                                                               mrp_action,
                                                               name)
                mrpmove_id = self.env['mrp.move'].create(move_data)
                qty_ordered = qty_ordered + qty

                if mrp_action == 'mo':
                    mrp_date_demand = mrp_date-timedelta(days=product.mrp_lead_time)
                    if mrp_date_demand < date.today():
                        mrp_date_demand = date.today()
                    if not product.product_id.bom_ids:
                        continue
                    bomcount = 0
                    for bom in product.product_id.bom_ids:
                        if not bom.active or not bom.bom_line_ids:
                            continue
                        bomcount += 1
                        if bomcount != 1:
                            continue
                        for bomline in bom.bom_line_ids:
                            if bomline.product_qty <= 0.00:
                                continue
                            if bomline.date_start and datetime.date(
                                    datetime.strptime(
                                        bomline.date_start, '%Y-%m-%d')) > \
                                    mrp_date_demand:
                                continue
                            if bomline.date_stop and datetime.date(
                                    datetime.strptime(
                                        bomline.date_stop, '%Y-%m-%d')) < \
                                    mrp_date_demand:
                                continue

                            mrp_date_demand_2 = mrp_date_demand-timedelta(
                                days=(product.mrp_transit_delay+product.
                                      mrp_inspection_delay))
                            move_data = \
                                self._prepare_mrp_move_data_bom_explosion(
                                    product, bomline, qty,
                                    mrp_date_demand_2,
                                    bom, name)
                            mrpmove_id2 = self.env['mrp.move'].create(
                                move_data)
                            sql_stat = "INSERT INTO mrp_move_rel (" \
                                       "move_up_id, " \
                                       "move_down_id) values (%d, %d)" % \
                                       (mrpmove_id, mrpmove_id2, )
                            self.env.cr.execute(sql_stat)
        values['qty_ordered'] = qty_ordered
        log_msg = '%s'  % qty_ordered
        logger.info(log_msg)
        return values

    @api.model
    def _mrp_cleanup(self):
        # Some part of the code with the new API is replaced by
        # sql statements due to performance issues when the auditlog is
        # installed
        logger.info('START MRP CLEANUP')
        self.env['mrp.move'].search([('id', '!=', 0)]).unlink()
        self.env['mrp.product'].search([('id', '!=', 0)]).unlink()
        logger.info('END MRP CLEANUP')
        return True

    @api.model
    def _low_level_code_calculation(self):
        logger.info('START LOW LEVEL CODE CALCULATION')
        counter = 999999
        sql_stat = 'update product_product set llc = 0'
        self.env.cr.execute(sql_stat)
        sql_stat = 'SELECT count(id) AS counter FROM product_product WHERE ' \
                   'llc = %d' % (0, )
        self.env.cr.execute(sql_stat)
        sql_res = self.env.cr.dictfetchone()
        if sql_res:
            counter = sql_res['counter']
        log_msg = 'LOW LEVEL CODE 0 FINISHED - NBR PRODUCTS: %s' % counter
        logger.info(log_msg)

        llc = 0
        # TODO: possibly replace condition to while counter != 0
        while counter != 999999:
            self.env.cr.commit()
            llc += 1
            sql_stat = """
                UPDATE product_product AS child_product 
                SET llc = %d
                FROM    mrp_bom_line AS bom_line, 
                        mrp_bom AS bom, 
                        product_product AS parent_product
                WHERE   child_product.llc = (%d - 1)
                        AND child_product.id = bom_line.product_id
                        AND bom_line.bom_id = bom.id
                        AND parent_product.product_tmpl_id = bom.product_tmpl_id
                        AND parent_product.llc = (%d - 1)
            """ % (llc, llc, llc, )
            self.env.cr.execute(sql_stat)
            sql_stat = 'SELECT count(id) AS counter FROM product_product ' \
                       'WHERE llc = %d' % (llc, )
            self.env.cr.execute(sql_stat)
            sql_res = self.env.cr.dictfetchone()
            if sql_res:
                counter = sql_res['counter']
            log_msg = 'LOW LEVEL CODE %s FINISHED - NBR PRODUCTS: %s' % (
                llc, counter)
            logger.info(log_msg)
            if counter == 0:
                counter = 999999
        mrp_lowest_llc = llc
        self.env.cr.commit()
        logger.info('END LOW LEVEL CODE CALCULATION')
        return mrp_lowest_llc

    @api.model
    def _calculate_mrp_applicable(self):
        logger.info('CALCULATE MRP APPLICABLE')
        sql_stat = '''UPDATE product_product SET mrp_applicable = False;'''
        self.env.cr.execute(sql_stat)

        sql_stat = """
            UPDATE product_product 
            SET mrp_applicable=True
            FROM product_template
            WHERE product_tmpl_id = product_template.id
                AND product_template.active = True
                AND product_template.type = 'product'
                AND mrp_minimum_stock > (
                    SELECT sum(quantity) FROM stock_quant, stock_location
                        WHERE stock_quant.product_id = product_product.id
                        AND stock_quant.location_id = stock_location.id
                        AND stock_location.usage = 'internal');"""
        self.env.cr.execute(sql_stat)

        sql_stat = """
            UPDATE product_product 
            SET mrp_applicable=True
            FROM product_template
            WHERE product_tmpl_id = product_template.id
                AND product_template.active = True
                AND product_template.type = 'product'
                AND product_product.id in (
                    SELECT distinct product_id 
                    FROM stock_move 
                    WHERE state <> 'draft' AND state <> 'cancel');"""
        self.env.cr.execute(sql_stat)

        sql_stat = """
            UPDATE product_product 
            SET mrp_applicable=True
            FROM product_template
            WHERE product_tmpl_id = product_template.id
                AND product_template.active = True
                AND product_template.type = 'product'
                AND llc > 0;"""
        self.env.cr.execute(sql_stat)

        sql_stat = """
            UPDATE product_product 
            SET mrp_applicable=True
            FROM mrp_forecast_product
            WHERE product_product.id = mrp_forecast_product.product_id;"""
        self.env.cr.execute(sql_stat)

        self.env.cr.commit()
        counter = 0
        sql_stat = """
            SELECT count(id) AS counter 
            FROM product_product 
            WHERE mrp_applicable = True"""
        self.env.cr.execute(sql_stat)
        sql_res = self.env.cr.dictfetchone()
        if sql_res:
            counter = sql_res['counter']
        log_msg = 'END CALCULATE MRP APPLICABLE: %s' % counter
        logger.info(log_msg)

    @api.model
    def _init_mrp_product(self, product, mrp_area):

        mrp_product_data = self._prepare_mrp_product_data(product,
                                                          mrp_area)
        return self.env['mrp.product'].create(mrp_product_data)

    @api.model
    def _init_mrp_move_from_forecast(self, mrp_product):
        forecast = self.env['mrp.forecast.product'].search(
            [('product_id', '=', mrp_product.product_id.id),
             ('mrp_area_id', '=', mrp_product.mrp_area_id.id)])
        for fc in forecast:
            for fc_id in fc.mrp_forecast_ids:
                mrp_move_data = \
                    self._prepare_mrp_move_data_from_forecast(
                        fc, fc_id, mrp_product)
                self.env['mrp.move'].create(mrp_move_data)
        return True

    @api.model
    def _init_mrp_move_from_stock_move(self, mrp_product):
        # TODO: Should we exclude the quantity done from the moves?
        move_obj = self.env['stock.move']
        mrp_move_obj = self.env['mrp.move']
        location_ids = self.env['stock.location'].search(
            [('id', 'child_of', mrp_product.mrp_area_id.location_id.id)])
        in_moves = move_obj.search(
            [('product_id', '=', mrp_product.product_id.id),
             ('state', '!=', 'done'),
             ('state', '!=', 'cancel'),
             ('product_qty', '>', 0.00),
             ('location_id', 'in', location_ids.ids)])
        out_moves = move_obj.search(
            [('product_id', '=', mrp_product.product_id.id),
             ('state', '!=', 'done'),
             ('state', '!=', 'cancel'),
             ('product_qty', '>', 0.00),
             ('location_dest_id', 'in', location_ids.ids)])
        moves = in_moves + out_moves
        for move in moves:
            move_data = self._prepare_mrp_move_data_from_stock_move(
                mrp_product, move)
            mrp_move_obj.create(move_data)
        return True

    # TODO: extension to purchase requisition in other module?
    @api.model
    def _prepare_mrp_move_data_from_purchase_requisition(self, preql,
                                                         mrp_product):
            mrp_date = date.today()
            if preql.requisition_id.schedule_date and \
                            datetime.date(datetime.strptime(
                                preql.requisition_id.schedule_date,
                                '%Y-%m-%d %H:%M:%S')) > date.today():
                mrp_date = datetime.date(datetime.strptime(
                    preql.requisition_id.schedule_date,
                    '%Y-%m-%d %H:%M:%S'))
            return {
                'product_id': preql.product_id.id,
                'mrp_product_id': mrp_product.id,
                'production_id': None,
                'purchase_order_id': None,
                'purchase_line_id': None,
                'sale_order_id': None,
                'sale_line_id': None,
                'stock_move_id': None,
                'mrp_qty': preql.product_qty,
                'current_qty': preql.product_qty,
                'mrp_date': mrp_date,
                'current_date': preql.requisition_id.schedule_date,
                'mrp_action': 'none',
                'mrp_type': 's',
                'mrp_processed': False,
                'mrp_origin': 'pr',
                'mrp_order_number': preql.requisition_id.name,
                'parent_product_id': None,
                'running_availability': 0.00,
                'name': preql.requisition_id.name,
                'state': preql.requisition_id.state,
            }

    # TODO: extension to purchase requisition in other module?
    @api.model
    def _init_mrp_move_from_purchase_requisition(self, mrp_product):
        location_ids = self.env['stock.location'].search(
            [('id', 'child_of', mrp_product.mrp_area_id.location_id.id)])
        picking_types = self.env['stock.picking.type'].search(
            [('default_location_dest_id', 'in', location_ids.ids)])
        picking_type_ids = [ptype.id for ptype in picking_types]
        requisitions = self.env['purchase.requisition'].search(
            [('picking_type_id', 'in', picking_type_ids),
             ('state', '=', 'draft')])
        req_lines = self.env['purchase.requisition.line'].search(
            [('requisition_id', 'in', requisitions.ids),
             ('product_qty', '>', 0.0),
             ('product_id', '=', mrp_product.product_id.id)])

        for preql in req_lines:
            mrp_move_data = \
                self._prepare_mrp_move_data_from_purchase_requisition(
                    preql, mrp_product)
            self.env['mrp.move'].create(mrp_move_data)

    @api.model
    def _prepare_mrp_move_data_from_purchase_order(self, poline, mrp_product):
        mrp_date = date.today()
        if fields.Date.from_string(poline.date_planned) > date.today():
            mrp_date = fields.Date.from_string(poline.date_planned)
        return {
            'product_id': poline.product_id.id,
            'mrp_product_id': mrp_product.id,
            'production_id': None,
            'purchase_order_id': poline.order_id.id,
            'purchase_line_id': poline.id,
            'sale_order_id': None,
            'sale_line_id': None,
            'stock_move_id': None,
            'mrp_qty': poline.product_qty,
            'current_qty': poline.product_qty,
            'mrp_date': mrp_date,
            'current_date': poline.date_planned,
            'mrp_action': 'none',
            'mrp_type': 's',
            'mrp_processed': False,
            'mrp_origin': 'po',
            'mrp_order_number': poline.order_id.name,
            'parent_product_id': None,
            'running_availability': 0.00,
            'name': poline.order_id.name,
            'state': poline.order_id.state,
        }

    @api.model
    def _init_mrp_move_from_purchase_order(self, mrp_product):
        location_ids = self.env['stock.location'].search(
            [('id', 'child_of', mrp_product.mrp_area_id.location_id.id)])
        picking_types = self.env['stock.picking.type'].search(
            [('default_location_dest_id', 'in',
              location_ids.ids)])
        picking_type_ids = [ptype.id for ptype in picking_types]
        orders = self.env['purchase.order'].search(
            [('picking_type_id', 'in', picking_type_ids),
             ('state', 'in', ['draft', 'confirmed'])])
        po_lines = self.env['purchase.order.line'].search(
            [('order_id', 'in', orders.ids),
             ('product_qty', '>', 0.0),
             ('product_id', '=', mrp_product.product_id.id)])

        for poline in po_lines:
            mrp_move_data = \
                self._prepare_mrp_move_data_from_purchase_order(
                    poline, mrp_product)
            self.env['mrp.move'].create(mrp_move_data)

    @api.model
    def _prepare_mrp_move_data_from_mrp_production(self, mo, mrp_product):
        mrp_date = date.today()
        if datetime.date(datetime.strptime(
                mo.date_planned, '%Y-%m-%d %H:%M:%S')) > date.today():
            mrp_date = datetime.date(datetime.strptime(
                mo.date_planned, '%Y-%m-%d %H:%M:%S'))
        return {
            'mrp_area_id': mrp_product.mrp_area_id.id,
            'product_id': mo.product_id.id,
            'mrp_product_id': mrp_product.id,
            'production_id': mo.id,
            'purchase_order_id': None,
            'purchase_line_id': None,
            'sale_order_id': None,
            'sale_line_id': None,
            'stock_move_id': None,
            'mrp_qty': mo.product_qty,
            'current_qty': mo.product_qty,
            'mrp_date': mrp_date,
            'current_date': mo.date_planned,
            'mrp_action': 'none',
            'mrp_type': 's',
            'mrp_processed': False,
            'mrp_origin': 'mo',
            'mrp_order_number': mo.name,
            'parent_product_id': None,
            'running_availability': 0.00,
            'name': mo.name,
            'state': mo.state,
        }

    @api.model
    def _prepare_mrp_move_data_from_mrp_production_bom(self, mo, bomline,
                                                       mrp_date_demand,
                                                       mrp_product):
        return {
            'mrp_area_id': mrp_product.mrp_area_id.id,
            'product_id': bomline.product_id.id,
            'mrp_product_id':
                bomline.product_id.mrp_product_id.id,
            'production_id': mo.id,
            'purchase_order_id': None,
            'purchase_line_id': None,
            'sale_order_id': None,
            'sale_line_id': None,
            'stock_move_id': None,
            'mrp_qty': -(mo.product_qty * bomline.product_qty),
            'current_qty': None,
            'mrp_date': mrp_date_demand,
            'current_date': None,
            'mrp_action': 'none',
            'mrp_type': 'd',
            'mrp_processed': False,
            'mrp_origin': 'mo',
            'mrp_order_number': mo.name,
            'parent_product_id': mo.product_id.id,
            'name': ('Demand Bom Explosion: ' + mo.name),
        }

    @api.model
    def _init_mrp_move_from_mrp_production_bom(self, mo, mrp_product):
        mrp_date = date.today()
        mrp_date_demand = mrp_date-timedelta(
            days=mrp_product.product_id.mrp_lead_time)
        if mrp_date_demand < date.today():
            mrp_date_demand = date.today()
        if mo.bom_id and mo.bom_id.bom_line_ids:
            for bomline in mo.bom_id.bom_line_ids:
                if bomline.product_qty <= 0.00:
                    continue
                if (bomline.date_start and datetime.date(
                        datetime.strptime(bomline.date_start, '%Y-%m-%d')) >=
                    mrp_date_demand):
                    continue
                if (bomline.date_stop and datetime.date(
                        datetime.strptime(bomline.date_stop, '%Y-%m-%d')) <=
                    mrp_date_demand):
                    continue
                mrp_move_data = \
                    self._prepare_mrp_move_data_from_mrp_production_bom(
                        mo, bomline, mrp_date_demand, mrp_product)
                self.env['mrp.move'].create(mrp_move_data)

    @api.model
    def _init_mrp_move_from_mrp_production(self, mrp_product):
        location_ids = self.env['stock.location'].search(
            [('id', 'child_of', mrp_product.mrp_area_id.location_id.id)])
        production_orders = self.env['mrp.production'].search(
            [('location_dest_id', 'in', location_ids.ids),
             ('product_qty', '>', 0.0),
             ('state', '=', 'draft')])
        for mo in production_orders:
            mrp_move_data = \
                self._prepare_mrp_move_data_from_mrp_production(
                    mo, mrp_product)
            self.env['mrp.move'].create(mrp_move_data)
            self._init_mrp_move_from_mrp_production_bom(mo, mrp_product)

    @api.model
    def _init_mrp_move(self, mrp_product):
        self._init_mrp_move_from_forecast(mrp_product)
        self._init_mrp_move_from_stock_move(mrp_product)
        # TODO: extension to purchase requisition in other module?
        # self._init_mrp_move_from_purchase_requisition(mrp_product)
        self._init_mrp_move_from_purchase_order(mrp_product)
        self._init_mrp_move_from_mrp_production(mrp_product)

    @api.model
    def _exclude_from_mrp(self, mrp_area, product):
        """ To extend with various logic where needed. """
        return product.mrp_exclude

    @api.model
    def _mrp_initialisation(self):
        logger.info('START MRP INITIALISATION')
        mrp_areas = self.env['mrp.area'].search([])
        products = self.env['product.product'].search([('mrp_applicable',
                                                        '=', True)])
        init_counter = 0
        for mrp_area in mrp_areas:
            for product in products:
                if self._exclude_from_mrp(mrp_area, product):
                    continue
                init_counter += 1
                log_msg = 'MRP INIT: %s - %s ' % (
                    init_counter, product.default_code)
                logger.info(log_msg)
                mrp_product = self._init_mrp_product(product, mrp_area)
                self._init_mrp_move(mrp_product)
                self.env.cr.commit()
        logger.info('END MRP INITIALISATION')

    @api.model
    def _init_mrp_move_grouped_demand(self, nbr_create, mrp_product):
        last_date = None
        last_qty = 0.00
        move_ids = []
        for move in mrp_product.mrp_move_ids:
            move_ids.append(move.id)
        for move_id in move_ids:
            move_rec = self.env['mrp.move'].search(
                [('id', '=', move_id)])
            for move in move_rec:
                if move.mrp_action == 'none':
                    if last_date is not None:
                        if datetime.date(
                                datetime.strptime(
                                    move.mrp_date, '%Y-%m-%d')) \
                                > last_date+timedelta(
                                    days=mrp_product.mrp_nbr_days):
                            if (onhand + last_qty + move.mrp_qty) \
                                    < mrp_product.mrp_minimum_stock \
                                    or (onhand + last_qty) \
                                    < mrp_product.mrp_minimum_stock:
                                name = 'Grouped Demand for ' \
                                       '%d Days' % (
                                    mrp_product.mrp_nbr_days, )
                                qtytoorder = \
                                    mrp_product.mrp_minimum_stock - \
                                    mrp_product - last_qty
                                cm = self.create_move(
                                    mrp_product_id=mrp_product.id,
                                    mrp_date=last_date,
                                    mrp_qty=qtytoorder,
                                    name=name)
                                qty_ordered = cm['qty_ordered']
                                onhand = onhand + last_qty + qty_ordered
                                last_date = None
                                last_qty = 0.00
                                nbr_create += 1
                    if (onhand + last_qty + move.mrp_qty) < \
                            mrp_product.mrp_minimum_stock or \
                                    (onhand + last_qty) < \
                                    mrp_product.mrp_minimum_stock:
                        if last_date is None:
                            last_date = datetime.date(
                                datetime.strptime(move.mrp_date,
                                                  '%Y-%m-%d'))
                            last_qty = move.mrp_qty
                        else:
                            last_qty = last_qty + move.mrp_qty
                    else:
                        last_date = datetime.date(
                            datetime.strptime(move.mrp_date,
                                              '%Y-%m-%d'))
                        onhand = onhand + move.mrp_qty

        if last_date is not None and last_qty != 0.00:
            name = 'Grouped Demand for %d Days' % \
                   (mrp_product.mrp_nbr_days, )
            qtytoorder = mrp_product.mrp_minimum_stock - onhand - last_qty
            cm = self.create_move(
                mrp_product_id=mrp_product.id, mrp_date=last_date,
                mrp_qty=qtytoorder, name=name)
            qty_ordered = cm['qty_ordered']
            onhand += qty_ordered
            nbr_create += 1
        return nbr_create

    @api.model
    def _mrp_calculation(self, mrp_lowest_llc):
        logger.info('START MRP CALCULATION')
        mrp_product_obj = self.env['mrp.product']
        counter = 0
        for mrp_area in self.env['mrp.area'].search([]):
            llc = 0
            while mrp_lowest_llc > llc:
                self.env.cr.commit()
                mrp_products = mrp_product_obj.search(
                    [('mrp_llc', '=', llc),
                     ('mrp_area_id', '=', mrp_area.id)])
                llc += 1

                for mrp_product in mrp_products:
                    nbr_create = 0
                    onhand = mrp_product.mrp_qty_available
                    if mrp_product.mrp_nbr_days == 0:
                        # todo: review ordering by date
                        for move in mrp_product.mrp_move_ids:
                            if move.mrp_action == 'none':
                                if (onhand + move.mrp_qty) < \
                                        mrp_product.mrp_minimum_stock:
                                    name = move.name
                                    qtytoorder = \
                                        mrp_product.mrp_minimum_stock - \
                                        onhand - move.mrp_qty
                                    cm = self.create_move(
                                        mrp_product_id=mrp_product.id,
                                        mrp_date=move.mrp_date,
                                        mrp_qty=qtytoorder, name=name)
                                    qty_ordered = cm['qty_ordered']
                                    onhand += move.mrp_qty + qty_ordered
                                    nbr_create += 1
                                else:
                                    onhand += move.mrp_qty
                    else:
                        nbr_create = self._init_mrp_move_grouped_demand(
                            nbr_create, mrp_product)

                    if onhand < mrp_product.mrp_minimum_stock and \
                            nbr_create == 0:
                        name = 'Minimum Stock'
                        qtytoorder = mrp_product.mrp_minimum_stock - onhand
                        cm = self.create_move(mrp_product_id=mrp_product.id,
                                              mrp_date=date.today(),
                                              mrp_qty=qtytoorder, name=name)
                        qty_ordered = cm['qty_ordered']
                        onhand += qty_ordered
                    counter += 1
                    self.env.cr.commit()
            log_msg = 'MRP CALCULATION LLC %s FINISHED - NBR PRODUCTS: %s' %(
                llc - 1, counter)
            logger.info(log_msg)
            if llc < 0:
                counter = 999999

        self.env.cr.commit()
        logger.info('END MRP CALCULATION')

    @api.model
    def _init_mrp_inventory(self, mrp_product):
        # Read Demand
        demand_qty_by_date = {}
        sql_stat = '''SELECT mrp_date, sum(mrp_qty) as demand_qty
                    FROM mrp_move
                    WHERE mrp_product_id = %d
                    AND mrp_type = 'd'
                    GROUP BY mrp_date''' % (mrp_product.id, )
        self.env.cr.execute(sql_stat)
        for sql_res in self.env.cr.dictfetchall():
            demand_qty_by_date[sql_res['mrp_date']] = sql_res['demand_qty']


        # Read Supply
        supply_qty_by_date = {}

        sql_stat = '''SELECT mrp_date, sum(mrp_qty) as supply_qty
                    FROM mrp_move
                    WHERE mrp_product_id = %d
                    AND mrp_type = 's'
                    AND mrp_action = 'none'
                    GROUP BY mrp_date''' % (mrp_product.id, )
        self.env.cr.execute(sql_stat)
        for sql_res in self.env.cr.dictfetchall():
            supply_qty_by_date[sql_res['mrp_date']] = sql_res['supply_qty']

        # Read supply actions
        supply_actions_qty_by_date = {}
        mrp_type = 's'
        exclude_mrp_actions = ['none', 'cancel']
        sql_stat = '''SELECT mrp_date, sum(mrp_qty) as actions_qty
                   FROM mrp_move
                   WHERE mrp_product_id = %d
                   AND mrp_qty <> 0.0
                   AND mrp_type = 's'
                   AND mrp_action not in %s
                   GROUP BY mrp_date''' % (mrp_product.id,
                                           tuple(exclude_mrp_actions))
        self.env.cr.execute(sql_stat)
        for sql_res in self.env.cr.dictfetchall():
            supply_actions_qty_by_date[sql_res['mrp_date']] = \
                sql_res['actions_qty']

        # Dates
        sql_stat = '''SELECT mrp_date
                    FROM mrp_move
                    WHERE mrp_product_id = %d
                    GROUP BY mrp_date
                    ORDER BY mrp_date''' % (mrp_product.id, )
        self.env.cr.execute(sql_stat)
        on_hand_qty = mrp_product.current_qty_available
        for sql_res in self.env.cr.dictfetchall():
            mdt = sql_res['mrp_date']
            mrp_inventory_data = {
                'mrp_product_id': mrp_product.id,
                'date': mdt,
            }
            demand_qty = 0.0
            supply_qty = 0.0
            if mdt in demand_qty_by_date.keys():
                demand_qty = demand_qty_by_date[mdt]
                mrp_inventory_data['demand_qty'] = abs(demand_qty)
            if mdt in supply_qty_by_date.keys():
                supply_qty = supply_qty_by_date[mdt]
                mrp_inventory_data['supply_qty'] = abs(supply_qty)
            if mdt in supply_actions_qty_by_date.keys():
                mrp_inventory_data['to_procure'] = \
                    supply_actions_qty_by_date[mdt]
            mrp_inventory_data['initial_on_hand_qty'] = on_hand_qty
            on_hand_qty += (supply_qty + demand_qty)
            mrp_inventory_data['final_on_hand_qty'] = on_hand_qty

            self.env['mrp.inventory'].create(mrp_inventory_data)

    @api.model
    def _mrp_final_process(self):
        logger.info('START MRP FINAL PROCESS')
        mrp_areas = self.env['mrp.area'].search([])
        mrp_product_ids = self.env['mrp.product'].search(
            [('mrp_llc', '<', 9999),
             ('mrp_area_id', 'in', mrp_areas.ids)])

        for mrp_product in mrp_product_ids:
            # Build the time-phased inventory
            self._init_mrp_inventory(mrp_product)

            # Complete the info on mrp_move
            qoh = mrp_product.mrp_qty_available
            nbr_actions = 0
            nbr_actions_4w = 0
            sql_stat = 'SELECT id, mrp_date, mrp_qty, mrp_action FROM ' \
                       'mrp_move WHERE mrp_product_id = %d ' \
                       'ORDER BY ' \
                       'mrp_date, ' \
                       'mrp_type desc, id' % (mrp_product.id, )
            self.env.cr.execute(sql_stat)
            for sql_res in self.env.cr.dictfetchall():
                qoh = qoh + sql_res['mrp_qty']
                self.env['mrp.move'].search(
                    [('id', '=', sql_res['id'])]).write(
                    {'running_availability': qoh})

            for move in mrp_product.mrp_move_ids:
                if move.mrp_action != 'none':
                    nbr_actions += 1
                if move.mrp_date:
                    if move.mrp_action != 'none' and \
                                    datetime.date(datetime.strptime(
                                        move.mrp_action_date, '%Y-%m-%d')) < \
                                            date.today()+timedelta(days=29):
                        nbr_actions_4w += 1
            if nbr_actions > 0:
                self.env['mrp.product'].search(
                    [('id', '=', mrp_product.id)]).write(
                    {'nbr_mrp_actions': nbr_actions,
                     'nbr_mrp_actions_4w': nbr_actions_4w})
            self.env.cr.commit()
        logger.info('END MRP FINAL PROCESS')

    @api.one
    def run_multi_level_mrp(self):
        self._mrp_cleanup()
        mrp_lowest_llc = self._low_level_code_calculation()
        self._calculate_mrp_applicable()
        self._mrp_initialisation()
        self._mrp_calculation(mrp_lowest_llc)
        self._mrp_final_process()
