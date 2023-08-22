import re

from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_subcontractor_partner = fields.Boolean(string="Subcontractor")
    subcontractor_resupply_warehouse_ids = fields.Many2many(
        comodel_name="stock.warehouse", string="Resupply from warehouse(s)"
    )
    partner_resupply_rule_warehouse_ids = fields.One2many(
        comodel_name="stock.rule", inverse_name="subcontracor_resuply_id", copy=False
    )
    subcontracted_created_location_id = fields.Many2one(
        comodel_name="stock.location", copy=False
    )
    partner_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type", copy=False
    )
    partner_buy_rule_id = fields.Many2one(comodel_name="stock.rule", copy=False)
    partner_resupply_rule_id = fields.Many2one(comodel_name="stock.rule", copy=False)

    @api.constrains("subcontractor_resupply_warehouse_ids")
    def _check_subcontractor_resupply_warehouse_ids(self):
        for rec in self:
            if (
                not rec.is_subcontractor_partner
                and rec.subcontractor_resupply_warehouse_ids
            ):
                raise models.UserError(
                    _(
                        "You can not edit 'Resupply from warehouse(s)' field, if partner is not Subcontractor"  # noqa
                    )
                )

    def action_subcontractor_location_stock(self):
        """Open subcontractor location stock list"""
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock.location_open_quants"
        )
        active_ids = self.property_stock_subcontractor.ids
        action.update(domain=[("location_id", "child_of", active_ids)])
        return action

    @api.model
    def get_data_struct(self):
        return {
            # Updating Subcontracting Location
            "subcontracted_created_location_id": "_create_subcontracting_location_data",
            # Updating Subcontracting operation type
            "partner_picking_type_id": "_create_operation_type_for_subcontracting",
            # Updating Route Rule for Subcontracting buy
            "partner_buy_rule_id": "_create_route_rule_for_subcontracting",
            # Updating Route Rule for Subcontracting resupply
            "partner_resupply_rule_id": "_create_route_rule_for_subcontracting_resupply",
        }

    def _set_active_subcontractor_warehouse(self, active):
        if not active:
            self.mapped("partner_resupply_rule_warehouse_ids").write({"active": active})
            return
        for rec in self:
            rec.with_context(
                active_test=False
            ).partner_resupply_rule_warehouse_ids.filtered(
                lambda r: r.warehouse_id in rec.subcontractor_resupply_warehouse_ids
            ).write(
                {"active": active}
            )

    def _set_subcontracting_values_active(self, active):
        """Set subcontracting values active/inactive by argument key"""
        for key in self.get_data_struct():
            self.mapped(key).write({"active": active})

    @api.model
    def _update_name_translation(self, records, name):
        """Update name field translation for records"""
        self.env["ir.translation"].search(
            [
                ("name", "=", "{},name".format(records._name)),
                ("res_id", "in", records.ids),
                ("value", "!=", name),
            ]
        ).write({"value": name})

    def _update_subcontractor_values_name(self, name):
        """
        Update subcontractor related records:
        - Location;
        - Operation type;
        - Route Rule for Subcontracting buy;
        - Route Rule for Subcontracting resupply.
        """
        partners = self.filtered(lambda p: p.is_subcontractor_partner)
        field_names = [*self.get_data_struct(), "property_stock_subcontractor"]
        field_names.remove("partner_picking_type_id")
        for field in field_names:
            records = partners.mapped(field)
            records.write({"name": name})
            self._update_name_translation(records, name)
        type_name = "%s:  IN" % name
        code = "".join(re.findall(r"\b\w", type_name))
        picks = partners.mapped("partner_picking_type_id")
        picks.write({"name": type_name, "sequence_code": code})
        self._update_name_translation(picks, type_name)

    def unlink(self):
        """This Method is override to archive all subcontracting field"""
        self._set_subcontracting_values_active(False)
        self._set_active_subcontractor_warehouse(False)
        return super(ResPartner, self).unlink()

    def write(self, vals):
        if "is_subcontractor_partner" in vals:
            self._update_subcontractor_entities_for_record(
                vals.get("is_subcontractor_partner")
            )
            self._set_active_subcontractor_warehouse(
                vals.get("is_subcontractor_partner")
            )
        if "active" in vals:
            self._set_subcontracting_values_active(vals.get("active"))
            self._set_active_subcontractor_warehouse(vals.get("active"))
        is_subcontract = vals.get("is_subcontractor_partner") is None
        check_subcontract = (
            self.is_subcontractor_partner
            if is_subcontract
            else vals.get("is_subcontractor_partner")
        )
        if "subcontractor_resupply_warehouse_ids" in vals and check_subcontract:
            wh_ids = self.subcontractor_resupply_warehouse_ids.ids
            vals.update(
                self._route_rule_for_subcontracting_resupply_warehouse(
                    vals, original_wh_ids=wh_ids
                )
                or {}
            )
        result = super(ResPartner, self).write(vals)
        if vals.get("name"):
            self._update_subcontractor_values_name(vals.get("name"))
        return result

    @api.model_create_multi
    def create(self, vals_list):
        check_data = self.get_data_struct().items()
        for vals in filter(
            lambda v: v.get("is_subcontractor_partner") and v.get("is_company"),
            vals_list,
        ):
            for key, func in check_data:
                if not getattr(self, key) or not vals.get(key):
                    vals.update(
                        **getattr(
                            self.with_context(partner_name=vals.get("name")), func
                        )(vals)
                        or {}
                    )
            if "subcontractor_resupply_warehouse_ids" in vals:
                vals.update(
                    self._route_rule_for_subcontracting_resupply_warehouse(vals) or {}
                )
        records = super(ResPartner, self).create(vals_list)
        for rec in records.filtered("partner_resupply_rule_warehouse_ids"):
            rec.partner_resupply_rule_warehouse_ids.write(
                {
                    "partner_address_id": rec.id,
                }
            )
        return records

    def _update_subcontractor_entities_for_record(self, is_subcontractor_partner):
        if not is_subcontractor_partner:
            return self._set_subcontracting_values_active(False)
        data_items = self.get_data_struct().items()
        for rec in self:
            vals = {}
            for key, record, func in map(
                lambda f: (f[0], getattr(rec, f[0]), f[1]), data_items
            ):
                if record:
                    record.active = True
                else:
                    if not getattr(rec, key) or not vals.get(key):
                        vals.update(**getattr(rec, func)(vals) or {})
            if vals:
                rec.write(vals)

    def _compose_entity_name(self):
        """
        Compose entity name. Override this function to implement onw logic
        :return: name (char) composed name
        """
        return self.display_name

    def _create_subcontracted_operation_type(self, vals):
        """Creating Operation Type for Subcontracting"""
        location_id = self._get_location_id_for_record(vals)
        if "partner_picking_type_id" in vals:
            return vals.get("partner_picking_type_id"), location_id
        if self.partner_picking_type_id:
            return self.partner_picking_type_id.id, location_id
        operation_type_name = "%s:  IN" % self._context.get(
            "partner_name", self._compose_entity_name()
        )
        operation_type_vals = {
            "name": operation_type_name,
            "code": "incoming",
            "sequence_code": "".join(re.findall(r"\b\w", operation_type_name)),
            "is_subcontractor": True,
        }
        company = self.company_id or self.env.company
        warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", company.id)], limit=1
        )
        if warehouse:
            operation_type_vals.update({"warehouse_id": warehouse.id})
        if location_id:
            operation_type_vals.update({"default_location_dest_id": location_id})
        return (
            self.env["stock.picking.type"].create(operation_type_vals).id,
            location_id,
        )

    def _get_location_id_for_record(self, vals):
        if "subcontracted_created_location_id" in vals:
            return vals.get("subcontracted_created_location_id")
        if self.subcontracted_created_location_id:
            return self.subcontracted_created_location_id.id
        company = self.company_id or self.env.company
        parent_location = (
            company.subcontracting_location_id and company.subcontracting_location_id.id
        )
        return (
            self.env["stock.location"]
            .create(
                {
                    "name": self._context.get(
                        "partner_name", self._compose_entity_name()
                    ),
                    "usage": "internal",
                    "location_id": parent_location or False,
                    "company_id": company.id,
                    "active": True,
                }
            )
            .id
        )

    def _create_subcontracting_location_data(self, vals):
        location_id = self._get_location_id_for_record(vals)
        return {
            "property_stock_subcontractor": location_id,
            "subcontracted_created_location_id": location_id,
        }

    def _create_operation_type_for_subcontracting(self, vals):
        # Creating Operation Type for Subcontracting starts here
        operation_type_rec_id, _ = self._create_subcontracted_operation_type(vals)
        return {"partner_picking_type_id": operation_type_rec_id}

    def _create_route_rule_for_subcontracting(self, vals):
        operation_type_rec_id, location_id = self._create_subcontracted_operation_type(
            vals
        )
        route = self.env.ref(
            "purchase_stock.route_warehouse0_buy", raise_if_not_found=False
        )
        buy_rule = self.env["stock.rule"].create(
            {
                "name": self._context.get("partner_name", self._compose_entity_name()),
                "action": "buy",
                "picking_type_id": operation_type_rec_id,
                "location_id": location_id,
                "route_id": route.id,
            }
        )
        return {"partner_buy_rule_id": buy_rule.id}

    def _create_route_rule_for_subcontracting_resupply(self, vals):
        prop = self.env["ir.property"]._get(
            "property_stock_production", "product.template"
        )
        picking_type = self.env.ref("stock.picking_type_out", raise_if_not_found=False)
        route = self.env.ref(
            "mrp_subcontracting.route_resupply_subcontractor_mto",
            raise_if_not_found=False,
        )
        rule = self.env["stock.rule"].create(
            {
                "name": self._context.get("partner_name", self._compose_entity_name()),
                "action": "pull",
                "partner_address_id": self._origin.id,
                "picking_type_id": picking_type.id,
                "location_id": prop.id,
                "location_src_id": self._get_location_id_for_record(vals),
                "route_id": route.id,
                "procure_method": "mts_else_mto",
            }
        )
        return {"partner_resupply_rule_id": rule.id}

    @api.model
    def _prepare_subcontractor_pull_from_stock_rule(
        self, warehouse, partner_name, location_id, partner_id
    ):
        """
        Prepare rule for subcontractor partner
        :param warehouse: stock.warehouse object
        :param partner_name: partner string name
        :param location_id: subcontracted location
        :param partner_id: Partner id
        :return: prepared stock.rule values
        """
        return {
            "name": "{}: Resupply {}".format(warehouse.name, partner_name),
            "action": "pull",
            "partner_address_id": partner_id,
            "picking_type_id": warehouse.out_type_id.id,
            "location_id": location_id,
            "location_src_id": warehouse.lot_stock_id.id,
            "route_id": warehouse.subcontracting_route_id.id,
            "procure_method": "mts_else_mto",
            "warehouse_id": warehouse.id,
        }

    def _route_rule_for_subcontracting_resupply_warehouse(
        self, vals, original_wh_ids=None
    ):
        original_wh_ids = original_wh_ids or []
        if "subcontractor_resupply_warehouse_ids" not in vals:
            return False
        record_ids = vals["subcontractor_resupply_warehouse_ids"][0][2]
        inactive_ids = set(original_wh_ids) - set(record_ids)
        if inactive_ids:
            # Deactivate warehouse rules
            self.partner_resupply_rule_warehouse_ids.filtered(
                lambda rule: rule.warehouse_id.id in inactive_ids
            ).write({"active": False})
        record_ids = list(set(record_ids) - set(original_wh_ids))
        warehouses = self.env["stock.warehouse"].browse(record_ids)
        if not warehouses.exists():
            return False
        partner_name = vals.get("name", self._compose_entity_name())
        location_id = (
            self.subcontracted_created_location_id.id
            if self
            else vals["subcontracted_created_location_id"]
        )
        result = []
        for warehouse in warehouses:
            if self:
                # Unarchive existing records
                rules = (
                    self.with_context(active_test=False)
                    .mapped("partner_resupply_rule_warehouse_ids")
                    .filtered(
                        lambda r: r.warehouse_id.id == warehouse.id and not r.active
                    )
                )
                if rules:
                    rules.write({"active": True})
                    continue
            # Prepare new rule for partner
            vals = self._prepare_subcontractor_pull_from_stock_rule(
                warehouse, partner_name, location_id, self.id
            )
            result.append((0, 0, vals))
        if not result:
            return False
        return {"partner_resupply_rule_warehouse_ids": result}
