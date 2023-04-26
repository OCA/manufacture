# Copyright 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# Copyright 2016-19 ForgeFlow S.L. (https://www.forgeflow.com)
# - Jordi Ballester Alomar <jordi.ballester@forgeflow.com>
# - Lois Rilo <lois.rilo@forgeflow.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging
from datetime import date, timedelta

from odoo import _, api, exceptions, fields, models
from odoo.tools import float_is_zero

logger = logging.getLogger(__name__)


class MultiLevelMrp(models.TransientModel):
    _name = "mrp.multi.level"
    _description = "Multi Level MRP"

    mrp_area_ids = fields.Many2many(
        comodel_name="mrp.area",
        string="MRP Areas to run",
        help="If empty, all areas will be computed.",
    )

    @api.model
    def _prepare_product_mrp_area_data(self, product_mrp_area):
        qty_available = 0.0
        product_obj = self.env["product.product"]
        location_ids = product_mrp_area.mrp_area_id._get_locations()
        for location in location_ids:
            product_l = product_obj.with_context({"location": location.id}).browse(
                product_mrp_area.product_id.id
            )
            qty_available += product_l.qty_available

        return {
            "product_mrp_area_id": product_mrp_area.id,
            "mrp_qty_available": qty_available,
            "mrp_llc": product_mrp_area.product_id.llc,
        }

    @api.model
    def _prepare_mrp_move_data_from_stock_move(
        self, product_mrp_area, move, direction="in"
    ):
        area = product_mrp_area.mrp_area_id
        if direction == "out":
            mrp_type = "d"
            product_qty = -move.product_qty
        else:
            mrp_type = "s"
            product_qty = move.product_qty
        po = po_line = None
        mo = origin = order_number = order_origin = parent_product_id = None
        if move.purchase_line_id:
            po = move.purchase_line_id.order_id
            order_number = po.name
            order_origin = po.origin
            origin = "po"
            po = move.purchase_line_id.order_id.id
            po_line = move.purchase_line_id.id
        elif move.production_id or move.raw_material_production_id:
            production = move.production_id or move.raw_material_production_id
            order_number = production.name
            order_origin = production.origin
            origin = "mo"
            mo = production.id
        elif move.move_dest_ids:
            for move_dest_id in move.move_dest_ids.filtered("production_id"):
                production = move_dest_id.production_id
                order_number = production.name
                order_origin = production.origin
                origin = "mo"
                mo = move_dest_id.production_id.id
                parent_product_id = (
                    move_dest_id.production_id.product_id or move_dest_id.product_id
                ).id
        if not order_number:
            source = (move.picking_id or move).origin
            order_number = source or (move.picking_id or move).name
            origin = "mv"
        # The date to display is based on the timezone of the warehouse.
        today_tz = area._datetime_to_date_tz()
        move_date_tz = area._datetime_to_date_tz(move.date_expected)
        if move_date_tz > today_tz:
            mrp_date = move_date_tz
        else:
            mrp_date = today_tz
        return {
            "product_id": move.product_id.id,
            "product_mrp_area_id": product_mrp_area.id,
            "production_id": mo,
            "purchase_order_id": po,
            "purchase_line_id": po_line,
            "stock_move_id": move.id,
            "mrp_qty": product_qty,
            "current_qty": product_qty,
            "mrp_date": mrp_date,
            "current_date": move.date_expected,
            "mrp_type": mrp_type,
            "mrp_origin": origin,
            "mrp_order_number": order_number,
            "parent_product_id": parent_product_id,
            "name": order_number,
            "origin": order_origin,
            "state": move.state,
        }

    @api.model
    def _prepare_planned_order_data(
        self, product_mrp_area, qty, mrp_date_supply, mrp_action_date, name, values
    ):
        return {
            "product_mrp_area_id": product_mrp_area.id,
            "mrp_qty": qty,
            "due_date": mrp_date_supply,
            "order_release_date": mrp_action_date,
            "mrp_action": product_mrp_area.supply_method,
            "qty_released": 0.0,
            "name": "Planned supply for: " + name,
            "origin": values.get("origin") or name,
            "fixed": False,
        }

    @api.model
    def _prepare_mrp_move_data_bom_explosion(
        self,
        product,
        bomline,
        qty,
        mrp_date_demand_2,
        bom,
        name,
        planned_order,
        values=None,
    ):
        product_mrp_area = self._get_product_mrp_area_from_product_and_area(
            bomline.product_id, product.mrp_area_id
        )
        if not product_mrp_area:
            raise exceptions.Warning(_("No MRP product found"))
        factor = (
            product.product_id.uom_id._compute_quantity(
                qty, bomline.bom_id.product_uom_id
            )
            / bomline.bom_id.product_qty
        )
        line_quantity = factor * bomline.product_qty
        return {
            "mrp_area_id": product.mrp_area_id.id,
            "product_id": bomline.product_id.id,
            "product_mrp_area_id": product_mrp_area.id,
            "production_id": None,
            "purchase_order_id": None,
            "purchase_line_id": None,
            "stock_move_id": None,
            "mrp_qty": -line_quantity,  # TODO: review with UoM
            "current_qty": None,
            "mrp_date": mrp_date_demand_2,
            "current_date": None,
            "mrp_type": "d",
            "mrp_origin": "mrp",
            "mrp_order_number": None,
            "parent_product_id": bom.product_id.id,
            "name": (
                "Demand Bom Explosion: %s"
                % (name or product.product_id.default_code or product.product_id.name)
            ).replace(
                "Demand Bom Explosion: Demand Bom Explosion: ", "Demand Bom Explosion: "
            ),
            "origin": planned_order.origin if planned_order else values.get("origin"),
        }

    @api.model
    def _get_action_and_supply_dates(self, product_mrp_area, mrp_date):
        if not isinstance(mrp_date, date):
            mrp_date = fields.Date.from_string(mrp_date)

        if mrp_date < date.today():
            mrp_date_supply = date.today()
        else:
            mrp_date_supply = mrp_date

        calendar = product_mrp_area.mrp_area_id.calendar_id
        if calendar and product_mrp_area.mrp_lead_time:
            date_str = fields.Date.to_string(mrp_date)
            dt = fields.Datetime.from_string(date_str)
            # dt is at the beginning of the day (00:00)
            res = calendar.plan_days(-1 * product_mrp_area.mrp_lead_time, dt)
            mrp_action_date = res.date()
        else:
            mrp_action_date = mrp_date - timedelta(days=product_mrp_area.mrp_lead_time)
        return mrp_action_date, mrp_date_supply

    @api.model
    def _get_bom_to_explode(self, product_mrp_area_id):
        boms = self.env["mrp.bom"]
        if product_mrp_area_id.supply_method in ["manufacture", "phantom"]:
            boms = product_mrp_area_id.product_id.bom_ids.filtered(
                lambda x: x.type in ["normal", "phantom"]
            )
        if not boms:
            return False
        return boms[0]

    @api.model
    def explode_action(
        self, product_mrp_area_id, mrp_action_date, name, qty, action, values=None
    ):
        """Explode requirements."""
        mrp_date_demand = mrp_action_date
        if mrp_date_demand < date.today():
            mrp_date_demand = date.today()
        bom = self._get_bom_to_explode(product_mrp_area_id)
        if not bom:
            return False
        pd = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        for bomline in bom.bom_line_ids:
            if (
                float_is_zero(bomline.product_qty, precision_digits=pd)
                or bomline.product_id.type != "product"
            ):
                continue
            if self.with_context(mrp_explosion=True)._exclude_from_mrp(
                bomline.product_id, product_mrp_area_id.mrp_area_id
            ):
                # Stop explosion.
                continue
            if bomline._skip_bom_line(product_mrp_area_id.product_id):
                continue
            # TODO: review: mrp_transit_delay, mrp_inspection_delay
            mrp_date_demand_2 = mrp_date_demand - timedelta(
                days=(
                    product_mrp_area_id.mrp_transit_delay
                    + product_mrp_area_id.mrp_inspection_delay
                )
            )
            move_data = self._prepare_mrp_move_data_bom_explosion(
                product_mrp_area_id,
                bomline,
                qty,
                mrp_date_demand_2,
                bom,
                name,
                action,
                values,
            )
            mrpmove_id2 = self.env["mrp.move"].create(move_data)
            if hasattr(action, "mrp_move_down_ids"):
                action.mrp_move_down_ids = [(4, mrpmove_id2.id)]
        return True

    @api.model
    def create_action(self, product_mrp_area_id, mrp_date, mrp_qty, name, values=None):
        if not values:
            values = {}
        if not isinstance(mrp_date, date):
            mrp_date = fields.Date.from_string(mrp_date)
        action_date, date_supply = self._get_action_and_supply_dates(
            product_mrp_area_id, mrp_date
        )
        return self.create_planned_order(
            product_mrp_area_id, mrp_qty, name, date_supply, action_date, values=values
        )

    @api.model
    def create_planned_order(
        self,
        product_mrp_area_id,
        mrp_qty,
        name,
        mrp_date_supply,
        mrp_action_date,
        values=None,
    ):
        self = self.with_context(auditlog_disabled=True)
        if self._exclude_from_mrp(
            product_mrp_area_id.product_id, product_mrp_area_id.mrp_area_id
        ):
            values["qty_ordered"] = 0.0
            return values

        qty_ordered = values.get("qty_ordered", 0.0) if values else 0.0
        qty_to_order = mrp_qty
        while qty_ordered < mrp_qty:
            qty = product_mrp_area_id._adjust_qty_to_order(qty_to_order)
            qty_to_order -= qty
            order_data = self._prepare_planned_order_data(
                product_mrp_area_id, qty, mrp_date_supply, mrp_action_date, name, values
            )
            # Do not create planned order for products that are Kits
            planned_order = False
            if not product_mrp_area_id.supply_method == "phantom":
                planned_order = self.env["mrp.planned.order"].create(order_data)
            qty_ordered = qty_ordered + qty

            if product_mrp_area_id._to_be_exploded():
                self.explode_action(
                    product_mrp_area_id,
                    mrp_action_date,
                    name,
                    qty,
                    planned_order,
                    values,
                )

        values["qty_ordered"] = qty_ordered
        log_msg = "[{}] {}: qty_ordered = {}".format(
            product_mrp_area_id.mrp_area_id.name,
            product_mrp_area_id.product_id.default_code
            or product_mrp_area_id.product_id.name,
            qty_ordered,
        )
        logger.debug(log_msg)
        return values

    @api.model
    def _mrp_cleanup(self, mrp_areas):
        logger.info("Start MRP Cleanup")
        domain = []
        if mrp_areas:
            domain += [("mrp_area_id", "in", mrp_areas.ids)]
        self.env["mrp.move"].search(domain).unlink()
        self.env["mrp.inventory"].search(domain).unlink()
        domain += [("fixed", "=", False)]
        self.env["mrp.planned.order"].search(domain).unlink()
        logger.info("End MRP Cleanup")
        return True

    def _domain_bom_lines_by_llc(self, llc, product_templates):
        return [
            ("product_id.llc", "=", llc),
            ("bom_id.product_tmpl_id", "in", product_templates.ids),
            ("bom_id.active", "=", True),
        ]

    def _get_bom_lines_by_llc(self, llc, product_templates):
        return self.env["mrp.bom.line"].search(
            self._domain_bom_lines_by_llc(llc, product_templates)
        )

    @api.model
    def _low_level_code_calculation(self):
        logger.info("Start low level code calculation")
        counter = 999999
        llc = 0
        llc_recursion_limit = (
            int(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("mrp_multi_level.llc_calculation_recursion_limit")
            )
            or 1000
        )
        self.env["product.product"].search([]).write({"llc": llc})
        products = self.env["product.product"].search([("llc", "=", llc)])
        if products:
            counter = len(products)
        log_msg = "Low level code 0 finished - Nbr. products: %s" % counter
        logger.info(log_msg)

        while counter:
            llc += 1
            products = self.env["product.product"].search([("llc", "=", llc - 1)])
            p_templates = products.mapped("product_tmpl_id")
            bom_lines = self._get_bom_lines_by_llc(llc - 1, p_templates)
            products = bom_lines.mapped("product_id")
            products.write({"llc": llc})
            counter = self.env["product.product"].search_count([("llc", "=", llc)])
            log_msg = "Low level code {} finished - Nbr. products: {}".format(
                llc, counter
            )
            logger.info(log_msg)
            if llc > llc_recursion_limit:
                logger.error("Recursion limit reached during LLC calculation.")
                break

        mrp_lowest_llc = llc
        logger.info("End low level code calculation")
        return mrp_lowest_llc

    @api.model
    def _adjust_mrp_applicable(self, mrp_areas):
        """This method is meant to modify the products that are applicable
           to MRP Multi level calculation
        """
        return True

    @api.model
    def _calculate_mrp_applicable(self, mrp_areas):
        logger.info("Start Calculate MRP Applicable")
        domain = []
        if mrp_areas:
            domain += [("mrp_area_id", "in", mrp_areas.ids)]
        self.env["product.mrp.area"].search(domain).write({"mrp_applicable": False})
        domain += [("product_id.type", "=", "product")]
        self.env["product.mrp.area"].search(domain).write({"mrp_applicable": True})
        self._adjust_mrp_applicable(mrp_areas)
        count_domain = [("mrp_applicable", "=", True)]
        if mrp_areas:
            count_domain += [("mrp_area_id", "in", mrp_areas.ids)]
        counter = self.env["product.mrp.area"].search(count_domain, count=True)
        log_msg = "End Calculate MRP Applicable: %s" % counter
        logger.info(log_msg)
        return True

    @api.model
    def _init_mrp_move_from_forecast(self, product_mrp_area):
        """This method is meant to be inherited to add a forecast mechanism."""
        return True

    @api.model
    def _init_mrp_move_from_stock_move(self, product_mrp_area):
        move_obj = self.env["stock.move"]
        mrp_move_obj = self.env["mrp.move"]
        in_domain = product_mrp_area._in_stock_moves_domain()
        in_moves = move_obj.search(in_domain)
        out_domain = product_mrp_area._out_stock_moves_domain()
        out_moves = move_obj.search(out_domain)
        if in_moves:
            for move in in_moves:
                move_data = self._prepare_mrp_move_data_from_stock_move(
                    product_mrp_area, move, direction="in"
                )
                if move_data:
                    mrp_move_obj.create(move_data)
        if out_moves:
            for move in out_moves:
                move_data = self._prepare_mrp_move_data_from_stock_move(
                    product_mrp_area, move, direction="out"
                )
                if move_data:
                    mrp_move_obj.create(move_data)
        return True

    @api.model
    def _prepare_mrp_move_data_from_purchase_order(self, poline, product_mrp_area):
        mrp_date = date.today()
        if fields.Date.from_string(poline.date_planned) > date.today():
            mrp_date = fields.Date.from_string(poline.date_planned)
        return {
            "product_id": poline.product_id.id,
            "product_mrp_area_id": product_mrp_area.id,
            "production_id": None,
            "purchase_order_id": poline.order_id.id,
            "purchase_line_id": poline.id,
            "stock_move_id": None,
            "mrp_qty": poline.product_uom_qty,
            "current_qty": poline.product_uom_qty,
            "mrp_date": mrp_date,
            "current_date": poline.date_planned,
            "mrp_type": "s",
            "mrp_origin": "po",
            "mrp_order_number": poline.order_id.name,
            "parent_product_id": None,
            "name": poline.order_id.name,
            "state": poline.order_id.state,
        }

    @api.model
    def _init_mrp_move_from_purchase_order(self, product_mrp_area):
        location_ids = product_mrp_area.mrp_area_id._get_locations()
        picking_types = self.env["stock.picking.type"].search(
            [("default_location_dest_id", "in", location_ids.ids)]
        )
        picking_type_ids = [ptype.id for ptype in picking_types]
        orders = self.env["purchase.order"].search(
            [
                ("picking_type_id", "in", picking_type_ids),
                ("state", "in", ["draft", "sent", "to approve"]),
            ]
        )
        po_lines = self.env["purchase.order.line"].search(
            [
                ("order_id", "in", orders.ids),
                ("product_qty", ">", 0.0),
                ("product_id", "=", product_mrp_area.product_id.id),
            ]
        )

        for line in po_lines:
            mrp_move_data = self._prepare_mrp_move_data_from_purchase_order(
                line, product_mrp_area
            )
            self.env["mrp.move"].create(mrp_move_data)

    @api.model
    def _get_product_mrp_area_from_product_and_area(self, product, mrp_area):
        return self.env["product.mrp.area"].search(
            [("product_id", "=", product.id), ("mrp_area_id", "=", mrp_area.id)],
            limit=1,
        )

    @api.model
    def _init_mrp_move(self, product_mrp_area):
        self._init_mrp_move_from_forecast(product_mrp_area)
        self._init_mrp_move_from_stock_move(product_mrp_area)
        self._init_mrp_move_from_purchase_order(product_mrp_area)

    @api.model
    def _exclude_from_mrp(self, product, mrp_area):
        """ To extend with various logic where needed. """
        product_mrp_area = self.env["product.mrp.area"].search(
            [("product_id", "=", product.id), ("mrp_area_id", "=", mrp_area.id)],
            limit=1,
        )
        if not product_mrp_area:
            return True
        return product_mrp_area.mrp_exclude

    @api.model
    def _mrp_initialisation(self, mrp_areas):
        logger.info("Start MRP initialisation")
        if not mrp_areas:
            mrp_areas = self.env["mrp.area"].search([])
        product_mrp_areas = self.env["product.mrp.area"].search(
            [("mrp_area_id", "in", mrp_areas.ids), ("mrp_applicable", "=", True)]
        )
        init_counter = 0
        for mrp_area in mrp_areas:
            for product_mrp_area in product_mrp_areas.filtered(
                lambda a: a.mrp_area_id == mrp_area
            ):
                if self._exclude_from_mrp(product_mrp_area.product_id, mrp_area):
                    continue
                init_counter += 1
                log_msg = "MRP Init: {} - {} ".format(
                    init_counter, product_mrp_area.display_name
                )
                logger.info(log_msg)
                self._init_mrp_move(product_mrp_area)
        logger.info("End MRP initialisation")

    @api.model
    def _init_mrp_move_grouped_demand(self, nbr_create, product_mrp_area):
        last_date = None
        last_qty = 0.00
        onhand = product_mrp_area.qty_available
        grouping_delta = product_mrp_area.mrp_nbr_days
        demand_origin = []
        for move in product_mrp_area.mrp_move_ids:
            if self._exclude_move(move):
                continue
            if (
                last_date
                and (
                    fields.Date.from_string(move.mrp_date)
                    >= last_date + timedelta(days=grouping_delta)
                )
                and (
                    (onhand + last_qty + move.mrp_qty)
                    < product_mrp_area.mrp_minimum_stock
                    or (onhand + last_qty) < product_mrp_area.mrp_minimum_stock
                )
            ):
                name = _(
                    "Grouped Demand of %(product_name)s for %(delta_days)d Days"
                ) % dict(
                    product_name=product_mrp_area.product_id.display_name,
                    delta_days=grouping_delta,
                )
                origin = ",".join(list(set(demand_origin)))
                qtytoorder = product_mrp_area.mrp_minimum_stock - onhand - last_qty
                cm = self.create_action(
                    product_mrp_area_id=product_mrp_area,
                    mrp_date=last_date,
                    mrp_qty=qtytoorder,
                    name=name,
                    values=dict(origin=origin),
                )
                qty_ordered = cm.get("qty_ordered", 0.0)
                onhand = onhand + last_qty + qty_ordered
                last_date = None
                last_qty = 0.00
                nbr_create += 1
                demand_origin = []
            if (
                (onhand + last_qty + move.mrp_qty) < product_mrp_area.mrp_minimum_stock
                or (onhand + last_qty) < product_mrp_area.mrp_minimum_stock
            ):
                if not last_date or last_qty == 0.0:
                    last_date = fields.Date.from_string(move.mrp_date)
                    last_qty = move.mrp_qty
                else:
                    last_qty += move.mrp_qty
            else:
                last_date = fields.Date.from_string(move.mrp_date)
                onhand += move.mrp_qty
            if move.mrp_type == "d":
                demand_origin.append(move.origin or move.name)

        if last_date and last_qty != 0.00:
            name = _(
                "Grouped Demand of %(product_name)s for %(delta_days)d Days"
            ) % dict(
                product_name=product_mrp_area.product_id.display_name,
                delta_days=grouping_delta,
            )
            origin = ",".join(list(set(demand_origin)))
            qtytoorder = product_mrp_area.mrp_minimum_stock - onhand - last_qty
            cm = self.create_action(
                product_mrp_area_id=product_mrp_area,
                mrp_date=last_date,
                mrp_qty=qtytoorder,
                name=name,
                values=dict(origin=origin),
            )
            qty_ordered = cm.get("qty_ordered", 0.0)
            onhand += qty_ordered
            nbr_create += 1
        return nbr_create

    @api.model
    def _exclude_move(self, move):
        """Improve extensibility being able to exclude special moves."""
        return False

    @api.model
    def _mrp_calculation(self, mrp_lowest_llc, mrp_areas):
        logger.info("Start MRP calculation")
        product_mrp_area_obj = self.env["product.mrp.area"]
        counter = 0
        if not mrp_areas:
            mrp_areas = self.env["mrp.area"].search([])
        for mrp_area in mrp_areas:
            llc = 0
            while mrp_lowest_llc > llc:
                product_mrp_areas = product_mrp_area_obj.search(
                    [("product_id.llc", "=", llc), ("mrp_area_id", "=", mrp_area.id)]
                )
                llc += 1

                for product_mrp_area in product_mrp_areas:
                    nbr_create = 0
                    onhand = product_mrp_area.qty_available
                    if product_mrp_area.mrp_nbr_days == 0:
                        for move in product_mrp_area.mrp_move_ids:
                            if self._exclude_move(move):
                                continue
                            qtytoorder = (
                                product_mrp_area.mrp_minimum_stock
                                - onhand
                                - move.mrp_qty
                            )
                            if qtytoorder > 0.0:
                                cm = self.create_action(
                                    product_mrp_area_id=product_mrp_area,
                                    mrp_date=move.mrp_date,
                                    mrp_qty=qtytoorder,
                                    name=move.name,
                                    values=dict(origin=move.origin),
                                )
                                qty_ordered = cm["qty_ordered"]
                                onhand += move.mrp_qty + qty_ordered
                                nbr_create += 1
                            else:
                                onhand += move.mrp_qty
                    else:
                        nbr_create = self._init_mrp_move_grouped_demand(
                            nbr_create, product_mrp_area
                        )

                    if onhand < product_mrp_area.mrp_minimum_stock and nbr_create == 0:
                        qtytoorder = product_mrp_area.mrp_minimum_stock - onhand
                        name = _("Safety Stock")
                        cm = self.create_action(
                            product_mrp_area_id=product_mrp_area,
                            mrp_date=date.today(),
                            mrp_qty=qtytoorder,
                            name=name,
                            values=dict(origin=name),
                        )
                        qty_ordered = cm["qty_ordered"]
                        onhand += qty_ordered
                    counter += 1

            log_msg = "MRP Calculation LLC {} Finished - Nbr. products: {}".format(
                llc - 1, counter
            )
            logger.info(log_msg)

        logger.info("Enb MRP calculation")

    @api.model
    def _get_demand_groups(self, product_mrp_area):
        query = """
            SELECT mrp_date, sum(mrp_qty)
            FROM mrp_move
            WHERE product_mrp_area_id = %(mrp_product)s
            AND mrp_type = 'd'
            GROUP BY mrp_date
        """
        params = {"mrp_product": product_mrp_area.id}
        return query, params

    @api.model
    def _get_supply_groups(self, product_mrp_area):
        query = """
                SELECT mrp_date, sum(mrp_qty)
                FROM mrp_move
                WHERE product_mrp_area_id = %(mrp_product)s
                AND mrp_type = 's'
                GROUP BY mrp_date
            """
        params = {"mrp_product": product_mrp_area.id}
        return query, params

    @api.model
    def _get_planned_order_groups(self, product_mrp_area):
        query = """
            SELECT due_date, sum(mrp_qty)
            FROM mrp_planned_order
            WHERE product_mrp_area_id = %(mrp_product)s
            GROUP BY due_date
        """
        params = {"mrp_product": product_mrp_area.id}
        return query, params

    @api.model
    def _prepare_mrp_inventory_data(
        self,
        product_mrp_area,
        mdt,
        on_hand_qty,
        running_availability,
        demand_qty_by_date,
        supply_qty_by_date,
        planned_qty_by_date,
    ):
        """Return dict to create mrp.inventory records on MRP Multi Level Scheduler"""
        mrp_inventory_data = {"product_mrp_area_id": product_mrp_area.id, "date": mdt}
        demand_qty = demand_qty_by_date.get(mdt, 0.0)
        mrp_inventory_data["demand_qty"] = abs(demand_qty)
        supply_qty = supply_qty_by_date.get(mdt, 0.0)
        mrp_inventory_data["supply_qty"] = abs(supply_qty)
        mrp_inventory_data["initial_on_hand_qty"] = on_hand_qty
        on_hand_qty += supply_qty + demand_qty
        mrp_inventory_data["final_on_hand_qty"] = on_hand_qty
        # Consider that MRP plan is followed exactly:
        running_availability += (
            supply_qty + demand_qty + planned_qty_by_date.get(mdt, 0.0)
        )
        mrp_inventory_data["running_availability"] = running_availability
        return mrp_inventory_data, running_availability, on_hand_qty

    @api.model
    def _init_mrp_inventory(self, product_mrp_area):
        mrp_move_obj = self.env["mrp.move"]
        planned_order_obj = self.env["mrp.planned.order"]
        # Read Demand
        demand_qty_by_date = {}
        query, params = self._get_demand_groups(product_mrp_area)
        self.env.cr.execute(query, params)
        for mrp_date, qty in self.env.cr.fetchall():
            demand_qty_by_date[mrp_date] = qty
        # Read Supply
        supply_qty_by_date = {}
        query, params = self._get_supply_groups(product_mrp_area)
        self.env.cr.execute(query, params)
        for mrp_date, qty in self.env.cr.fetchall():
            supply_qty_by_date[mrp_date] = qty
        # Read planned orders:
        planned_qty_by_date = {}
        query, params = self._get_planned_order_groups(product_mrp_area)
        self.env.cr.execute(query, params)
        for mrp_date, qty in self.env.cr.fetchall():
            planned_qty_by_date[mrp_date] = qty
        # Dates
        moves_dates = mrp_move_obj.search(
            [("product_mrp_area_id", "=", product_mrp_area.id)], order="mrp_date"
        ).mapped("mrp_date")
        action_dates = planned_order_obj.search(
            [("product_mrp_area_id", "=", product_mrp_area.id)], order="due_date"
        ).mapped("due_date")
        mrp_dates = set(moves_dates + action_dates)
        on_hand_qty = product_mrp_area.product_id.with_context(
            location=product_mrp_area.mrp_area_id.location_id.id
        )._product_available()[product_mrp_area.product_id.id]["qty_available"]
        running_availability = on_hand_qty
        for mdt in sorted(mrp_dates):
            (
                mrp_inventory_data,
                running_availability,
                on_hand_qty,
            ) = self._prepare_mrp_inventory_data(
                product_mrp_area,
                mdt,
                on_hand_qty,
                running_availability,
                demand_qty_by_date,
                supply_qty_by_date,
                planned_qty_by_date,
            )
            inv_id = self.env["mrp.inventory"].create(mrp_inventory_data)
            # attach planned orders to inventory
            planned_order_obj.search(
                [
                    ("due_date", "=", mdt),
                    ("product_mrp_area_id", "=", product_mrp_area.id),
                ]
            ).write({"mrp_inventory_id": inv_id.id})

    @api.model
    def _mrp_final_process(self, mrp_areas):
        logger.info("Start MRP final process")
        domain = [("product_id.llc", "<", 9999)]
        if mrp_areas:
            domain += [("mrp_area_id", "in", mrp_areas.ids)]
        product_mrp_area_ids = self.env["product.mrp.area"].search(domain)

        for product_mrp_area in product_mrp_area_ids:
            # Build the time-phased inventory
            if (
                self._exclude_from_mrp(
                    product_mrp_area.product_id, product_mrp_area.mrp_area_id
                )
                or product_mrp_area.supply_method == "phantom"
            ):
                continue
            self._init_mrp_inventory(product_mrp_area)
        logger.info("End MRP final process")

    def run_mrp_multi_level(self):
        self._mrp_cleanup(self.mrp_area_ids)
        mrp_lowest_llc = self._low_level_code_calculation()
        self._calculate_mrp_applicable(self.mrp_area_ids)
        self._mrp_initialisation(self.mrp_area_ids)
        self._mrp_calculation(mrp_lowest_llc, self.mrp_area_ids)
        self._mrp_final_process(self.mrp_area_ids)
        # Open MRP inventory screen to show result if manually run:
        action = self.env.ref("mrp_multi_level.mrp_inventory_action")
        result = action.read()[0]
        return result
