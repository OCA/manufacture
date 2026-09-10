from markupsafe import Markup, escape

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MrpWorkorderAssignSubcontract(models.TransientModel):
    _name = "mrp.workorder.assign.subcontract"
    _description = "Wizard - Assign Workorder To Subcontract"

    @api.model
    def _get_all_flow_type_selection(self):
        return {
            "standard": "Standard",
            "urgent": "Urgent",
            "subcontractor_stock": "Subcontractor stock",
        }

    @api.model
    def _get_allowed_flow_type_keys(self):
        allowed_flow_types = {"standard"}
        if self.env.user.has_group(
            "mrp_workorder_subcontracting.group_flow_type_urgent"
        ):
            allowed_flow_types.add("urgent")
        if self.env.user.has_group(
            "mrp_workorder_subcontracting.group_flow_type_subcontractor_stock"
        ):
            allowed_flow_types.add("subcontractor_stock")
        return allowed_flow_types

    @api.model
    def _get_flow_type_selection(self):
        all_flow_types = self._get_all_flow_type_selection()
        return [
            (key, label)
            for key, label in all_flow_types.items()
            if key in self._get_allowed_flow_type_keys()
        ]

    @api.model
    def default_get(self, fields_list):
        values = super().default_get(fields_list)
        workorder_ids = self.env.context.get(
            "default_workorder_ids"
        ) or self.env.context.get("active_ids", [])
        workorders = self.env["mrp.workorder"].browse(workorder_ids)
        if not workorders:
            return values
        if any(w.has_subcontract_documents for w in workorders):
            raise ValidationError(
                _(
                    "Some selected work orders already have subcontracting "
                    "documents generated.\n"
                    "You cannot generate them again."
                )
            )
        common_partner_ids = set(workorders[:1].subcontract_partner_ids.ids)
        for workorder in workorders[1:]:
            common_partner_ids &= set(workorder.subcontract_partner_ids.ids)
        if common_partner_ids and "partner_ids" in fields_list:
            values["partner_ids"] = [(6, 0, sorted(common_partner_ids))]

        service_ids = {
            workorder.subcontract_product_id.id
            for workorder in workorders
            if workorder.subcontract_product_id
        }
        if (
            len(service_ids) == 1
            and len(service_ids) == len(workorders)
            and "service_id" in fields_list
        ):
            values["service_id"] = next(iter(service_ids))
        return values

    workorder_ids = fields.Many2many(
        comodel_name="mrp.workorder", string="Workorders", required=True
    )
    partner_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Suppliers",
        required=True,
    )
    has_multiple_partners = fields.Boolean(
        string="Has Multiple Suppliers",
        compute="_compute_has_multiple_partners",
    )
    date_finished = fields.Datetime(string="Scheduled Date Finished", required=True)
    flow_type = fields.Selection(
        selection=_get_flow_type_selection,
        default="standard",
        string="Flow type",
        required=True,
    )
    create_purchase_order = fields.Boolean(
        string="Create new purchase order?", default=False
    )
    purchase_order_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Purchase Order",
        domain=[("state", "in", ["draft", "sent", "to_approve"])],
    )
    service_id = fields.Many2one(
        comodel_name="product.product",
        string="Service purchase",
        domain=[("type", "=", "service"), ("purchase_ok", "=", True)],
    )
    type_id = fields.Many2one(
        comodel_name="purchase.order.type",
        string="Purchase Type",
    )
    urgent_note = fields.Text(string="Reason for urgency")

    @api.depends("partner_ids")
    def _compute_has_multiple_partners(self):
        for wizard in self:
            wizard.has_multiple_partners = len(wizard.partner_ids) > 1

    def assign(self):
        self.ensure_one()
        self._apply_subcontract_bid_defaults()
        # Backend validation for group access
        self._validate_flow_type_access()
        # Backend validation for compiled fields
        self._validate_wizard_fields()
        # Backend validation for configuration fields
        self._validate_selected_workorders()
        # Registration of note for urgency in production order
        self._update_production_urgent_note()
        if self.flow_type == "standard":
            return self._assign_standard_flow()
        return self._assign_stock_flow()

    @api.onchange("purchase_order_id")
    def _onchange_purchase_order_id(self):
        # Align partners of purchase order
        if self.purchase_order_id:
            self.partner_ids = [(6, 0, self.purchase_order_id.partner_id.ids)]

    @api.onchange("partner_ids", "flow_type")
    def _onchange_subcontract_bid_rules(self):
        self._apply_subcontract_bid_defaults()

    @api.onchange("create_purchase_order")
    def _onchange_create_purchase_order(self):
        if self.create_purchase_order:
            self.purchase_order_id = False

    @api.onchange("flow_type")
    def _onchange_flow_type_reset_purchase_order(self):
        self._apply_subcontract_bid_defaults()

    def _apply_subcontract_bid_defaults(self):
        for wizard in self:
            if len(wizard.partner_ids) > 1:
                wizard.flow_type = "standard"
                wizard.create_purchase_order = True
                wizard.purchase_order_id = False

    @api.constrains("flow_type")
    def _constrain_flow_type_access(self):
        self._validate_flow_type_access()

    def _validate_flow_type_access(self):
        all_flow_types = self._get_all_flow_type_selection()
        allowed_flow_types = self._get_allowed_flow_type_keys()
        for wizard in self:
            if wizard.flow_type and wizard.flow_type not in allowed_flow_types:
                raise ValidationError(
                    _("You are not allowed to select the flow type '%s'.")
                    % all_flow_types.get(wizard.flow_type, wizard.flow_type)
                )

    def _validate_wizard_fields(self):
        for wizard in self:
            wizard._validate_required_wizard_fields()
            if wizard.flow_type == "standard":
                wizard._validate_standard_flow_fields()
                continue
            wizard._validate_non_standard_flow_fields()

    def _validate_required_wizard_fields(self):
        self.ensure_one()
        if not self.partner_ids:
            raise ValidationError(_("At least one supplier is required."))
        if not self.date_finished:
            raise ValidationError(_("Scheduled Date Finished is required."))
        if len(self.partner_ids) > 1 and self.flow_type != "standard":
            raise ValidationError(
                _(
                    "Multiple suppliers are only allowed for the standard "
                    "subcontracting flow."
                )
            )
        if self.flow_type == "urgent" and not self.urgent_note:
            raise ValidationError(_("Reason for urgency is required for urgent flow."))
        if (
            self.create_purchase_order or self.purchase_order_id
        ) and not self.service_id:
            raise ValidationError(_("Service purchase is required."))
        if self.create_purchase_order and not self.type_id:
            raise ValidationError(
                _("Purchase Type is required when creating a new purchase order.")
            )

    def _validate_standard_flow_fields(self):
        self.ensure_one()
        flow_labels = self._get_all_flow_type_selection()
        if len(self.partner_ids) > 1 and not self.create_purchase_order:
            raise ValidationError(
                _(
                    "When multiple suppliers are selected, you must create new "
                    "requests for quotation."
                )
            )
        if (
            len(self.partner_ids) <= 1
            and not self.create_purchase_order
            and not self.purchase_order_id
        ):
            raise ValidationError(
                _("An existing purchase order is required for flow '%s'.")
                % flow_labels[self.flow_type]
            )
        if not self.create_purchase_order:
            self._validate_existing_purchase_order_supplier()

    def _validate_non_standard_flow_fields(self):
        self.ensure_one()
        if len(self.partner_ids) > 1 and (
            self.create_purchase_order or self.purchase_order_id
        ):
            raise ValidationError(
                _(
                    "Purchase order options are only available with one supplier "
                    "for non-standard subcontracting flows."
                )
            )
        if self.purchase_order_id:
            self._validate_existing_purchase_order_supplier()

    def _validate_existing_purchase_order_supplier(self):
        self.ensure_one()
        if len(self.partner_ids) != 1:
            raise ValidationError(
                _(
                    "Exactly one supplier is required when using an existing "
                    "purchase order."
                )
            )
        if self.purchase_order_id.partner_id not in self.partner_ids:
            raise ValidationError(
                _(
                    "The selected purchase order supplier must match the "
                    "selected supplier."
                )
            )

    def _validate_selected_workorders(self):
        self.ensure_one()
        warehouses = self._get_workorder_warehouses()
        if not warehouses:
            raise ValidationError(
                _("Unable to determine the warehouse from the selected work orders.")
            )
        if len(warehouses) > 1:
            raise ValidationError(
                _("Selected work orders belong to different warehouses.")
            )

        for workorder in self.workorder_ids:
            if not workorder.subcontract_ok:
                raise ValidationError(
                    _("Work order '%s' is not marked as subcontracting.")
                    % workorder.display_name
                )
            allowed_partners = workorder.subcontract_partner_ids
            invalid_partners = self.partner_ids - allowed_partners
            if allowed_partners and invalid_partners:
                raise ValidationError(
                    _("Some selected suppliers are not allowed for work order '%s'.")
                    % workorder.display_name
                )
            if workorder.qty_remaining <= 0:
                raise ValidationError(
                    _("Work order '%s' has no remaining quantity to process.")
                    % workorder.display_name
                )
            if (
                self.flow_type == "standard"
                or self.create_purchase_order
                or self.purchase_order_id
            ) and workorder.purchase_order_line_ids:
                raise ValidationError(
                    _("Work order '%s' is already linked to a purchase order line.")
                    % workorder.display_name
                )
            if self.flow_type == "urgent" and workorder.delivery_move_ids.filtered(
                lambda move: move.state != "cancel"
            ):
                raise ValidationError(
                    _("Work order '%s' already has delivery moves.")
                    % workorder.display_name
                )
            if (
                self.flow_type == "subcontractor_stock"
                and workorder.return_move_ids.filtered(
                    lambda move: move.state != "cancel"
                )
            ):
                raise ValidationError(
                    _("Work order '%s' already has return moves.")
                    % workorder.display_name
                )

        if self.create_purchase_order or self.purchase_order_id:
            self._validate_purchase_order_type_configuration()
        if self.flow_type != "standard":
            self._validate_workorder_warehouse_configuration()

    def _validate_workorder_warehouse_configuration(self):
        warehouse = self._get_workorder_warehouses()[:1]
        if not warehouse.sub_out_picking_type_id:
            raise ValidationError(
                _("Warehouse '%s' is missing Subcontract Picking Type OUT.")
                % warehouse.display_name
            )
        if not warehouse.sub_in_picking_type_id:
            raise ValidationError(
                _("Warehouse '%s' is missing Subcontract Picking Type IN.")
                % warehouse.display_name
            )
        if not warehouse.sub_out_virtual_picking_type_id:
            raise ValidationError(
                _("Warehouse '%s' is missing Subcontract Virtual Picking Type OUT.")
                % warehouse.display_name
            )
        if not warehouse.sub_in_virtual_picking_type_id:
            raise ValidationError(
                _("Warehouse '%s' is missing Subcontract Virtual Picking Type IN.")
                % warehouse.display_name
            )

    def _validate_purchase_order_type_configuration(self):
        for wizard in self:
            purchase_order_type = wizard._get_purchase_order_type_to_use()
            if not purchase_order_type:
                if wizard.create_purchase_order:
                    continue
                raise ValidationError(
                    _(
                        "The selected purchase order '%s' has no Purchase Type "
                        "configured."
                    )
                    % wizard.purchase_order_id.display_name
                )
            if not purchase_order_type.is_subcontracting:
                raise ValidationError(
                    _("Purchase Type '%s' is not marked as subcontracting.")
                    % purchase_order_type.display_name
                )
            if wizard.flow_type != "standard":
                continue
            if not purchase_order_type.sub_out_picking_type_id:
                raise ValidationError(
                    _("Purchase Type '%s' is missing Subcontract OUT Picking Type.")
                    % purchase_order_type.display_name
                )
            if not purchase_order_type.sub_in_picking_type_id:
                raise ValidationError(
                    _("Purchase Type '%s' is missing Subcontract IN Picking Type.")
                    % purchase_order_type.display_name
                )

    def _get_workorder_warehouses(self):
        return self.mapped("workorder_ids.production_id.picking_type_id.warehouse_id")

    def _get_purchase_order_type_to_use(self):
        self.ensure_one()
        if self.create_purchase_order:
            return self.type_id
        return self.purchase_order_id.order_type

    def _assign_standard_flow(self):
        """Standard flow logics:
        Purchase order line -> Delivery -> Return of goods
        This is the standard flow of the subcontract.
        Only the purchase order line is created for subsequent documents.
        """
        partner_purchase_orders, purchase_orders = (
            self._get_purchase_orders_by_partner()
        )

        for workorder in self.workorder_ids:
            self._update_workorder_subcontracting_values(workorder)
            for partner in self.partner_ids:
                purchase_order = partner_purchase_orders.get(partner.id)
                if not purchase_order:
                    continue
                self.env["purchase.order.line"].create(
                    self._prepare_purchase_order_line_vals(purchase_order, workorder)
                )

        return self._get_purchase_order_action(purchase_orders)

    def _get_purchase_orders_by_partner(self):
        purchase_orders = self.env["purchase.order"]
        partner_purchase_orders = {}
        if self.create_purchase_order:
            for partner in self.partner_ids:
                purchase_order = self.env["purchase.order"].create(
                    self._prepare_purchase_order_vals(partner)
                )
                partner_purchase_orders[partner.id] = purchase_order
                purchase_orders |= purchase_order
        elif self.purchase_order_id:
            partner_purchase_orders[self.purchase_order_id.partner_id.id] = (
                self.purchase_order_id
            )
            purchase_orders |= self.purchase_order_id
        return partner_purchase_orders, purchase_orders

    def _prepare_purchase_order_vals(self, partner):
        currency_id = (
            partner.property_purchase_currency_id.id or self.env.company.currency_id.id
        )
        return {
            "partner_id": partner.id,
            "date_planned": self.date_finished,
            "order_type": self.type_id.id,
            "subcontract_location_id": (
                partner.property_stock_subcontract_location_id.id
                or partner.property_stock_virtual_subcontract_location_id.id
            ),
            "origin": _("Subcontracting"),
            "payment_term_id": partner.property_supplier_payment_term_id.id,
            "fiscal_position_id": partner.property_account_position_id.id,
            "currency_id": currency_id,
        }

    def _prepare_purchase_order_line_vals(self, purchase_order, workorder):
        self.ensure_one()
        return {
            "order_id": purchase_order.id,
            "product_id": self.service_id.id,
            "product_qty": workorder.qty_remaining,
            "product_uom": self.service_id.uom_po_id.id,
            "price_unit": 0,
            "date_planned": self.date_finished,
            "name": self._get_purchase_order_line_description(workorder),
            "workorder_id": workorder.id,
        }

    def _get_purchase_order_line_description(self, workorder):
        self.ensure_one()
        return f"{workorder.production_id.display_name} - {workorder.name}"

    def _update_workorder_subcontracting_values(self, workorder, partner=False):
        vals = {}
        if self.partner_ids and set(workorder.subcontract_partner_ids.ids) != set(
            self.partner_ids.ids
        ):
            vals["subcontract_partner_ids"] = [(6, 0, self.partner_ids.ids)]
        if self.service_id and workorder.subcontract_product_id != self.service_id:
            vals["subcontract_product_id"] = self.service_id.id
        if workorder.subcontract_flow_type != self.flow_type:
            vals["subcontract_flow_type"] = self.flow_type
        if vals:
            workorder.write(vals)
        if partner and workorder.subcontracting_flow == "parts":
            workorder._sync_subcontract_raw_move_location(partner)

    def _update_production_urgent_note(self):
        if self.flow_type != "urgent" or not self.urgent_note:
            return
        productions = self.workorder_ids.mapped("production_id")
        for production in productions:
            workorders = self.workorder_ids.filtered(
                lambda workorder, production=production: (
                    workorder.production_id == production
                )
            )
            body = Markup("<b>%s</b><br/>%s<br/>%s<br/>%s") % (
                escape(_("Urgent subcontracting")),
                escape(_("User: %s") % self.env.user.display_name),
                escape(_("Reason: %s") % self.urgent_note),
                escape(_("Workorders: %s") % ", ".join(workorders.mapped("name"))),
            )
            production.message_post(body=body, subtype_xmlid="mail.mt_note")

    def _assign_stock_flow(self):
        """Stock flow logics:
        Purchase order line <-> Delivery -> Return of goods
        Create and link stock pickings for subcontracting flows.

        This method only generates delivery/return pickings and related moves
        based on the selected flow type.
        """
        self.ensure_one()
        created_pickings = self.env["stock.picking"]
        partner_purchase_orders, purchase_orders = (
            self._get_purchase_orders_by_partner()
            if self.create_purchase_order or self.purchase_order_id
            else ({}, self.env["purchase.order"])
        )
        for partner in self.partner_ids:
            for workorder in self.workorder_ids:
                self._update_workorder_subcontracting_values(workorder, partner=partner)
                purchase_order_line = self.env["purchase.order.line"]
                purchase_order = partner_purchase_orders.get(partner.id)
                if purchase_order:
                    purchase_order_line = self.env["purchase.order.line"].create(
                        self._prepare_purchase_order_line_vals(
                            purchase_order, workorder
                        )
                    )
                picking = self._get_or_create_picking_for_workorder(workorder, partner)
                move_values = self._prepare_stock_move_vals(workorder, picking)
                created_moves = self.env["stock.move"].create(move_values)
                if self.flow_type == "urgent":
                    created_moves.write({"sub_delivery_workorder_id": workorder.id})
                else:
                    created_moves.write({"sub_return_workorder_id": workorder.id})
                if purchase_order_line:
                    created_moves.write(
                        {"sub_purchase_line_id": purchase_order_line.id}
                    )
                created_moves._action_confirm(merge=False)
                created_pickings |= picking

        for picking in created_pickings:
            if picking.state == "draft":
                picking.action_confirm()
            if self.flow_type == "urgent":
                picking.action_assign()
        return self._get_picking_action(created_pickings)

    def _get_or_create_picking_for_workorder(self, workorder, partner):
        picking_type, location_id, location_dest_id = self._get_picking_config(
            workorder, partner
        )
        picking = self._find_open_picking(
            picking_type, workorder.subcontracting_flow, partner
        )
        if picking:
            return picking
        return self.env["stock.picking"].create(
            {
                "partner_id": partner.id,
                "picking_type_id": picking_type.id,
                "location_id": location_id.id,
                "location_dest_id": location_dest_id.id,
                "origin": _("Subcontracting %s") % workorder.production_id.display_name,
                "scheduled_date": self.date_finished,
            }
        )

    def _find_open_picking(self, picking_type, subcontracting_flow, partner):
        pickings = self.env["stock.picking"].search(
            [
                ("partner_id", "=", partner.id),
                ("picking_type_id", "=", picking_type.id),
                ("state", "not in", ["done", "cancel"]),
            ],
            order="scheduled_date,id",
        )
        return pickings.filtered(
            lambda picking: (
                (subcontracting_flow == "parts" and picking.subcontract_parts)
                or (subcontracting_flow == "finished" and not picking.subcontract_parts)
            )
        )[:1]

    def _get_picking_config(self, workorder, partner):
        warehouse = self._get_workorder_warehouses()[:1]
        if self.flow_type == "urgent":
            if workorder.subcontracting_flow == "parts":
                picking_type = warehouse.sub_out_picking_type_id
                location_id = picking_type.default_location_src_id
                location_dest_id = (
                    partner.property_stock_subcontract_location_id
                    or picking_type.default_location_dest_id
                )
            else:
                picking_type = warehouse.sub_out_virtual_picking_type_id
                location_id = picking_type.default_location_src_id
                location_dest_id = (
                    partner.property_stock_virtual_subcontract_location_id
                    or picking_type.default_location_dest_id
                )
        else:
            if workorder.subcontracting_flow == "parts":
                picking_type = warehouse.sub_in_picking_type_id
                location_id = picking_type.default_location_src_id
                location_dest_id = picking_type.default_location_dest_id
            else:
                picking_type = warehouse.sub_in_virtual_picking_type_id
                location_id = (
                    partner.property_stock_virtual_subcontract_location_id
                    or picking_type.default_location_src_id
                )
                location_dest_id = picking_type.default_location_dest_id
        if not location_id or not location_dest_id:
            raise ValidationError(
                _("Missing subcontracting locations for work order '%s'.")
                % workorder.display_name
            )
        return picking_type, location_id, location_dest_id

    def _prepare_stock_move_vals(self, workorder, picking):
        if self.flow_type == "subcontractor_stock":
            return [self._prepare_finished_move_vals(workorder, picking)]
        if workorder.subcontracting_flow == "parts":
            return self._prepare_component_move_vals(workorder, picking)
        return [self._prepare_finished_move_vals(workorder, picking)]

    def _prepare_component_move_vals(self, workorder, picking):
        move_values = []
        factor = (
            workorder.qty_remaining / workorder.qty_production
            if workorder.qty_production
            else 0
        )
        for raw_move in workorder._get_subcontract_component_moves().filtered(
            lambda move: move.state not in ("done", "cancel")
        ):
            qty = raw_move.product_uom_qty * factor
            if qty <= 0:
                continue
            move_values.append(
                {
                    "name": raw_move.display_name or raw_move.product_id.display_name,
                    "product_id": raw_move.product_id.id,
                    "product_uom": raw_move.product_uom.id,
                    "product_uom_qty": qty,
                    "location_id": picking.location_id.id,
                    "location_dest_id": picking.location_dest_id.id,
                    "picking_id": picking.id,
                    "origin": workorder.production_id.display_name,
                    "company_id": picking.company_id.id,
                    "warehouse_id": picking.picking_type_id.warehouse_id.id,
                }
            )
        if not move_values:
            raise ValidationError(
                _("No raw material moves available for work order '%s'.")
                % workorder.display_name
            )
        return move_values

    def _prepare_finished_move_vals(self, workorder, picking):
        return {
            "name": workorder.product_id.display_name,
            "product_id": workorder.product_id.id,
            "product_uom": workorder.product_uom_id.id,
            "product_uom_qty": workorder.qty_remaining,
            "location_id": picking.location_id.id,
            "location_dest_id": picking.location_dest_id.id,
            "picking_id": picking.id,
            "origin": workorder.production_id.display_name,
            "company_id": picking.company_id.id,
            "warehouse_id": picking.picking_type_id.warehouse_id.id,
        }

    def _get_picking_action(self, pickings):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        if len(pickings) == 1:
            action.update(
                {
                    "view_mode": "form",
                    "views": [(self.env.ref("stock.view_picking_form").id, "form")],
                    "res_id": pickings.id,
                }
            )
            action.pop("domain", None)
            return action
        action["domain"] = [("id", "in", pickings.ids)]
        return action

    def _get_purchase_order_action(self, purchase_orders):
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_rfq")
        if len(purchase_orders) == 1:
            action.update(
                {
                    "view_mode": "form",
                    "views": [
                        (self.env.ref("purchase.purchase_order_form").id, "form")
                    ],
                    "res_id": purchase_orders.id,
                }
            )
            action.pop("domain", None)
            return action
        action["domain"] = [("id", "in", purchase_orders.ids)]
        return action
