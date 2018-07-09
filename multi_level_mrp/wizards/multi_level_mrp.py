# © 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# Copyright 2016-18 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar <jordi.ballester@eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import date, datetime, timedelta
import logging

logger = logging.getLogger(__name__)

ODOO_READ_GROUP_DAY_FORMAT = '%d %b %Y'


class MultiLevelMrp(models.TransientModel):
    _name = 'multi.level.mrp'

    # TODO: dates are not being correctly computed for supply...

    @api.model
    def _prepare_mrp_product_data(self, product, mrp_area):
        qty_available = 0.0
        product_obj = self.env['product.product']
        # TODO: move mrp_qty_available computation, maybe unreserved??
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
            'name': product.name,
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
    def _prepare_mrp_move_data_from_stock_move(
            self, mrp_product, move, direction='in'):
        # TODO: Clean up to reduce dependencies
        if not((move.location_id.usage == 'internal' and
                move.location_dest_id.usage != 'internal') \
                or (move.location_id.usage != 'internal' and
                            move.location_dest_id.usage == 'internal')):
            # TODO: not sure about this...
            return {}
        if direction == 'out':
            mrp_type = 'd'
            product_qty = -move.product_qty
        else:
            mrp_type = 's'
            product_qty = move.product_qty
        po = po_line = so = so_line = None
        mo = origin = order_number = parent_product_id = None
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
            # TODO: move.move_dest_id -> move.move_dest_ids. DONE, review
            if move.move_dest_ids:
                # move_dest_id = move.move_dest_ids[:1]
                for move_dest_id in move.move_dest_ids:
                    if move_dest_id.production_id:
                        order_number = move_dest_id.production_id.name
                        origin = 'mo'
                        mo = move_dest_id.production_id.id
                        if move_dest_id.production_id.product_id:
                            parent_product_id = \
                                move_dest_id.production_id.product_id.id
                        else:
                            parent_product_id = move_dest_id.product_id.id
        if order_number is None:
            order_number = move.name
        mrp_date = date.today()
        if datetime.date(datetime.strptime(
                move.date_expected,
                DEFAULT_SERVER_DATETIME_FORMAT)) > date.today():
            mrp_date = datetime.date(datetime.strptime(
                move.date_expected, DEFAULT_SERVER_DATETIME_FORMAT))
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
            'mrp_qty': product_qty,
            'current_qty': product_qty,
            'mrp_date': mrp_date,
            'current_date': move.date_expected,
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

    @api.model
    def _prepare_mrp_move_data_supply(
            self, mrp_product, qty, mrp_date_supply, mrp_action_date,
            mrp_action, name):
        return {
            'mrp_area_id': mrp_product.mrp_area_id.id,
            'product_id': mrp_product.product_id.id,
            'mrp_product_id': mrp_product.id,
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
    def _prepare_mrp_move_data_bom_explosion(
            self, product, bomline, qty, mrp_date_demand_2, bom, name):
        mrp_product = self._get_mrp_product_from_product_and_area(
            bomline.product_id, product.mrp_area_id)
        if not mrp_product:
            raise exceptions.Warning(
                _("No MRP product found"))

        return {
            'mrp_area_id': product.mrp_area_id.id,
            'product_id': bomline.product_id.id,
            'mrp_product_id': mrp_product.id,
            'production_id': None,
            'purchase_order_id': None,
            'purchase_line_id': None,
            'sale_order_id': None,
            'sale_line_id': None,
            'stock_move_id': None,
            'mrp_qty': -(qty * bomline.product_qty),  # TODO: review with UoM
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
            mrp_date = fields.Date.from_string(mrp_date)

        if mrp_product_id.supply_method == 'buy':
            # if mrp_product_id.purchase_requisition:
            #     mrp_action = 'pr'
            # else:
            mrp_action = 'po'
        else:
            # TODO: consider 'none'...
            mrp_action = 'mo'

        if mrp_date < date.today():
            mrp_date_supply = date.today()
        else:
            mrp_date_supply = mrp_date

        mrp_action_date = mrp_date - timedelta(
            days=mrp_product_id.mrp_lead_time)

        qty_ordered = 0.00
        qty_to_order = mrp_qty
        while qty_ordered < mrp_qty:
            qty = mrp_product_id._adjust_qty_to_order(qty_to_order)
            qty_to_order -= qty
            move_data = self._prepare_mrp_move_data_supply(
                mrp_product_id, qty, mrp_date_supply, mrp_action_date,
                mrp_action, name)
            mrpmove_id = self.env['mrp.move'].create(move_data)
            qty_ordered = qty_ordered + qty

            if mrp_action == 'mo':
                mrp_date_demand = mrp_date - timedelta(
                    days=mrp_product_id.mrp_lead_time)
                if mrp_date_demand < date.today():
                    mrp_date_demand = date.today()
                if not mrp_product_id.product_id.bom_ids:
                    continue
                bomcount = 0
                for bom in mrp_product_id.product_id.bom_ids:
                    if not bom.active or not bom.bom_line_ids:
                        continue
                    bomcount += 1
                    if bomcount != 1:
                        continue
                    for bomline in bom.bom_line_ids:
                        if bomline.product_qty <= 0.00:
                            continue
                        if self._exclude_from_mrp(
                                mrp_product_id.mrp_area_id, bomline.product_id):
                            # Stop explosion.
                            continue
                        mrp_date_demand_2 = mrp_date_demand - timedelta( # TODO: review this...
                            days=(mrp_product_id.mrp_transit_delay +
                                  mrp_product_id.mrp_inspection_delay))
                        move_data = \
                            self._prepare_mrp_move_data_bom_explosion(
                                mrp_product_id, bomline, qty,
                                mrp_date_demand_2,
                                bom, name)
                        mrpmove_id2 = self.env['mrp.move'].create(move_data)
                        sql_stat = "INSERT INTO mrp_move_rel (" \
                                   "move_up_id, " \
                                   "move_down_id) values (%d, %d)" % \
                                   (mrpmove_id, mrpmove_id2, )
                        self.env.cr.execute(sql_stat)
        values['qty_ordered'] = qty_ordered
        log_msg = '%s' % qty_ordered
        logger.info(log_msg)
        return values

    @api.model
    def _mrp_cleanup(self):
        # Some part of the code with the new API is replaced by
        # sql statements due to performance issues when the auditlog is
        # installed
        logger.info('START MRP CLEANUP')
        self.env['mrp.move'].search([]).unlink()
        self.env['mrp.product'].search([]).unlink()
        self.env['mrp.inventory'].search([]).unlink()
        logger.info('END MRP CLEANUP')
        return True

    @api.model
    def _low_level_code_calculation(self):
        logger.info('START LOW LEVEL CODE CALCULATION')
        counter = 999999
        llc = 0
        self.env['product.product'].search([]).write({'llc': llc})
        products = self.env['product.product'].search([('llc', '=', llc)])
        if products:
            counter = len(products)
        log_msg = 'LOW LEVEL CODE 0 FINISHED - NBR PRODUCTS: %s' % counter
        logger.info(log_msg)

        while counter:
            llc += 1
            products = self.env['product.product'].search(
                [('llc', '=', llc - 1)])
            p_templates = products.mapped('product_tmpl_id')
            bom_lines = self.env['mrp.bom.line'].search(
                [('product_id.llc', '=', llc - 1),
                 ('bom_id.product_tmpl_id', 'in', p_templates.ids)])
            products = bom_lines.mapped('product_id')
            products.write({'llc': llc})
            products = self.env['product.product'].search([('llc', '=', llc)])
            counter = len(products)
            log_msg = 'LOW LEVEL CODE %s FINISHED - NBR PRODUCTS: %s' % (
                llc, counter)
            logger.info(log_msg)

        mrp_lowest_llc = llc
        logger.info('END LOW LEVEL CODE CALCULATION')
        return mrp_lowest_llc

    @api.model
    def _calculate_mrp_applicable(self):
        # TODO: Refactor all code here
        self.env['product.product'].search([
            ('type', '=', 'product'),
        ]).write({'mrp_applicable': True})
        return True
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

        # self.env.cr.commit()
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

        mrp_product_data = self._prepare_mrp_product_data(
            product, mrp_area)
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

    # TODO: move this methods to mrp_product?? to be able to show moves with an action
    @api.model
    def _in_stock_moves_domain(self, mrp_product):
        locations = self.env['stock.location'].search(
            [('id', 'child_of', mrp_product.mrp_area_id.location_id.id)])
        return [
            ('product_id', '=', mrp_product.product_id.id),
            ('state', 'not in', ['done', 'cancel']),
            ('product_qty', '>', 0.00),
            ('location_id', 'not in', locations.ids),
            ('location_dest_id', 'in', locations.ids),
        ]

    @api.model
    def _out_stock_moves_domain(self, mrp_product):
        locations = self.env['stock.location'].search(
            [('id', 'child_of', mrp_product.mrp_area_id.location_id.id)])
        return [
            ('product_id', '=', mrp_product.product_id.id),
            ('state', 'not in', ['done', 'cancel']),
            ('product_qty', '>', 0.00),
            ('location_id', 'in', locations.ids),
            ('location_dest_id', 'not in', locations.ids),
        ]

    @api.model
    def _init_mrp_move_from_stock_move(self, mrp_product):
        # TODO: Should we exclude the quantity done from the moves?
        move_obj = self.env['stock.move']
        mrp_move_obj = self.env['mrp.move']
        in_domain = self._in_stock_moves_domain(mrp_product)
        in_moves = move_obj.search(in_domain)
        out_domain = self._out_stock_moves_domain(mrp_product)
        out_moves = move_obj.search(out_domain)
        if in_moves:
            for move in in_moves:
                move_data = self._prepare_mrp_move_data_from_stock_move(
                    mrp_product, move, direction='in')
                mrp_move_obj.create(move_data)
        if out_moves:
            for move in out_moves:
                move_data = self._prepare_mrp_move_data_from_stock_move(
                    mrp_product, move, direction='out')
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
             ('state', 'in', ['draft', 'sent', 'to approve'])])
        po_lines = self.env['purchase.order.line'].search(
            [('order_id', 'in', orders.ids),
             ('product_qty', '>', 0.0),
             ('product_id', '=', mrp_product.product_id.id)])

        for line in po_lines:
            mrp_move_data = \
                self._prepare_mrp_move_data_from_purchase_order(
                    line, mrp_product)
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
    def _get_mrp_product_from_product_and_area(self, product, mrp_area):
        return self.env['mrp.product'].search([
            ('product_id', '=', product.id),
            ('mrp_area_id', '=', mrp_area.id),
        ], limit=1)

    @api.model
    def _prepare_mrp_move_data_from_mrp_production_bom(
            self, mo, bomline, mrp_date_demand, mrp_product):
        line_mrp_product = self._get_mrp_product_from_product_and_area(
                bomline.product_id, mrp_product.mrp_area_id)
        return {
            'mrp_area_id': mrp_product.mrp_area_id.id,
            'product_id': bomline.product_id.id,
            'mrp_product_id': line_mrp_product.id,
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
        # TODO: iniciate this from moves with MOs and for other moves from bom lines??
        # TODO: fix this...
        # mrp_date = date.today()
        # mrp_date_demand = mrp_date - timedelta(
        #     days=mrp_product.product_id.produce_delay)
        # if mrp_date_demand < date.today():
        #     mrp_date_demand = date.today()
        mrp_date_demand = date.today()
        if mo.bom_id and mo.bom_id.bom_line_ids:
            for bomline in mo.bom_id.bom_line_ids:
                if bomline.product_qty <= 0.00:
                    continue
                # TODO: ['mrp.bom.line'].date_start does not exist in v11. Remove:
                # if (bomline.date_start and datetime.date(
                #         datetime.strptime(bomline.date_start, '%Y-%m-%d')) >=
                #         mrp_date_demand):
                #     continue
                # if (bomline.date_stop and datetime.date(
                #         datetime.strptime(bomline.date_stop, '%Y-%m-%d')) <=
                #         mrp_date_demand):
                #     continue
                # TODO: add conditions to do this: ddmrp, not already existing MOs (MTO)...
                mrp_move_data = \
                    self._prepare_mrp_move_data_from_mrp_production_bom(
                        mo, bomline, mrp_date_demand, mrp_product)
                self.env['mrp.move'].create(mrp_move_data)

    @api.model
    def _init_mrp_move_from_mrp_production(self, mrp_product):
        location_ids = self.env['stock.location'].search(
            [('id', 'child_of', mrp_product.mrp_area_id.location_id.id)])
        # TODO: there is no 'draft' state anymore. there will always be stock.moves
        production_orders = self.env['mrp.production'].search([
            ('product_id', '=', mrp_product.product_id.id),
            ('location_dest_id', 'in', location_ids.ids),
            ('product_qty', '>', 0.0),
            ('state', 'in', ['confirmed', 'planned']),
        ])  # TODO: 'progress' as well?
        for mo in production_orders:
            # mrp_move_data = \
            #     self._prepare_mrp_move_data_from_mrp_production(
            #         mo, mrp_product)
            # self.env['mrp.move'].create(mrp_move_data)
            self._init_mrp_move_from_mrp_production_bom(mo, mrp_product)

    @api.model
    def _init_mrp_move(self, mrp_product):
        self._init_mrp_move_from_forecast(mrp_product)
        self._init_mrp_move_from_stock_move(mrp_product)
        # TODO: extension to purchase requisition in other module?
        # self._init_mrp_move_from_purchase_requisition(mrp_product)
        self._init_mrp_move_from_purchase_order(mrp_product)
        # TODO: not needed I think... check case when MO are partially done and posted...
        # self._init_mrp_move_from_mrp_production(mrp_product)

    @api.model
    def _exclude_from_mrp(self, mrp_area, product):
        """ To extend with various logic where needed. """
        return product.mrp_exclude

    @api.model
    def _mrp_initialisation(self):
        logger.info('START MRP INITIALISATION')
        mrp_areas = self.env['mrp.area'].search([])
        products = self.env['product.product'].search([
            ('mrp_applicable', '=', True)])
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
            # for mrp_product in self.env['mrp.product'].search([]):
                self._init_mrp_move(mrp_product)
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
                mrp_products = mrp_product_obj.search(
                    [('mrp_llc', '=', llc),
                     ('mrp_area_id', '=', mrp_area.id)])
                llc += 1

                for mrp_product in mrp_products:
                    nbr_create = 0
                    onhand = mrp_product.mrp_qty_available # TODO: qty unreserved?
                    if mrp_product.mrp_nbr_days == 0:
                        # todo: review ordering by date
                        for move in mrp_product.mrp_move_ids:
                            if move.mrp_action == 'none':
                                if (onhand + move.mrp_qty) < \
                                        mrp_product.mrp_minimum_stock:
                                    qtytoorder = \
                                        mrp_product.mrp_minimum_stock - \
                                        onhand - move.mrp_qty
                                    cm = self.create_move(
                                        mrp_product_id=mrp_product,
                                        mrp_date=move.mrp_date,
                                        mrp_qty=qtytoorder, name=move.name)
                                    qty_ordered = cm['qty_ordered']
                                    onhand += move.mrp_qty + qty_ordered
                                    nbr_create += 1
                                else:
                                    onhand += move.mrp_qty
                    else:
                        # TODO: review this
                        nbr_create = self._init_mrp_move_grouped_demand(
                            nbr_create, mrp_product)

                    if onhand < mrp_product.mrp_minimum_stock and \
                            nbr_create == 0:
                        qtytoorder = mrp_product.mrp_minimum_stock - onhand
                        cm = self.create_move(
                            mrp_product_id=mrp_product,
                            mrp_date=date.today(),
                            mrp_qty=qtytoorder,
                            name='Minimum Stock')
                        qty_ordered = cm['qty_ordered']
                        onhand += qty_ordered
                    counter += 1

            log_msg = 'MRP CALCULATION LLC %s FINISHED - NBR PRODUCTS: %s' % (
                llc - 1, counter)
            logger.info(log_msg)

        logger.info('END MRP CALCULATION')

    @api.model
    def _init_mrp_inventory(self, mrp_product):
        mrp_move_obj = self.env['mrp.move']
        # Read Demand
        demand_groups = mrp_move_obj.read_group(
            [('mrp_product_id', '=', mrp_product.id),
             ('mrp_type', '=', 'd')],
            ['mrp_date', 'mrp_qty'], ['mrp_date:day'],
        )
        demand_qty_by_date = {}
        for group in demand_groups:
            # Reformat date back to default server format.
            group_date = datetime.strptime(
                group['mrp_date:day'], ODOO_READ_GROUP_DAY_FORMAT).strftime(
                DEFAULT_SERVER_DATE_FORMAT)
            demand_qty_by_date[group_date] = group['mrp_qty']

        # Read Supply
        supply_groups = mrp_move_obj.read_group(
            [('mrp_product_id', '=', mrp_product.id),
             ('mrp_type', '=', 's'),
             ('mrp_action', '=', 'none')],
            ['mrp_date', 'mrp_qty'], ['mrp_date:day'],
        )
        supply_qty_by_date = {}
        for group in supply_groups:
            # Reformat date back to default server format.
            group_date = datetime.strptime(
                group['mrp_date:day'], ODOO_READ_GROUP_DAY_FORMAT).strftime(
                DEFAULT_SERVER_DATE_FORMAT)
            supply_qty_by_date[group_date] = group['mrp_qty']

        # Read supply actions
        # TODO: if we remove cancel take it into account here,
        # TODO: as well as mrp_type ('r').
        exclude_mrp_actions = ['none', 'cancel']
        action_groups = mrp_move_obj.read_group(
            [('mrp_product_id', '=', mrp_product.id),
             ('mrp_qty', '!=', 0.0),
             ('mrp_type', '=', 's'),
             ('mrp_action', 'not in', exclude_mrp_actions)],
            ['mrp_date', 'mrp_qty'], ['mrp_date:day'],
        )
        supply_actions_qty_by_date = {}
        for group in action_groups:
            # Reformat date back to default server format.
            group_date = datetime.strptime(
                group['mrp_date:day'], ODOO_READ_GROUP_DAY_FORMAT).strftime(
                DEFAULT_SERVER_DATE_FORMAT)
            supply_actions_qty_by_date[group_date] = group['mrp_qty']

        # Dates
        mrp_dates = set(mrp_move_obj.search([
            ('mrp_product_id', '=', mrp_product.id)],
            order='mrp_date').mapped('mrp_date'))

        on_hand_qty = mrp_product.current_qty_available  # TODO: unreserved?
        for mdt in sorted(mrp_dates):
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
        mrp_product_ids = self.env['mrp.product'].search([
            ('mrp_llc', '<', 9999),
            ('mrp_area_id', '!=', False)])

        for mrp_product in mrp_product_ids:
            # Build the time-phased inventory
            self._init_mrp_inventory(mrp_product)

            # Complete info on mrp_move (running availability and nbr actions)
            qoh = mrp_product.mrp_qty_available

            moves = self.env['mrp.move'].search([
                ('mrp_product_id', '=', mrp_product.id)],
                order='mrp_date, mrp_type desc, id')
            for move in moves:
                qoh = qoh + move.mrp_qty
                move.running_availability = qoh

            nbr_actions = mrp_product.mrp_move_ids.filtered(
                lambda m: m.mrp_action != 'none')
            horizon_4w = fields.Date.to_string(
                date.today() + timedelta(weeks=4))
            nbr_actions_4w = nbr_actions.filtered(
                lambda m: m.mrp_action_date < horizon_4w)
            if nbr_actions:
                mrp_product.write({
                    'nbr_mrp_actions': len(nbr_actions),
                    'nbr_mrp_actions_4w': len(nbr_actions_4w),
                })
        logger.info('END MRP FINAL PROCESS')

    @api.multi
    def run_multi_level_mrp(self):
        self._mrp_cleanup()
        mrp_lowest_llc = self._low_level_code_calculation()
        self._calculate_mrp_applicable()
        self._mrp_initialisation()
        self._mrp_calculation(mrp_lowest_llc)
        self._mrp_final_process()
