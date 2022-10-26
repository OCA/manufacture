from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_subcontractor_partner = fields.Boolean(string="Subcontractor")
    subcontracted_created_location_id = fields.Many2one(
        copy=False, comodel_name="stock.location"
    )
    partner_picking_type_id = fields.Many2one(
        copy=False, comodel_name="stock.picking.type"
    )
    partner_buy_rule_id = fields.Many2one(
        copy=False,
        comodel_name="stock.rule",
    )
    partner_resupply_rule_id = fields.Many2one(
        copy=False,
        comodel_name="stock.rule",
    )

    def _set_subcontracting_values_active(self, active):
        self.ensure_one()
        if self.subcontracted_created_location_id:
            self.subcontracted_created_location_id.active = active
        if self.partner_picking_type_id:
            self.partner_picking_type_id.active = active
        if self.partner_buy_rule_id:
            self.partner_buy_rule_id.active = active
        if self.partner_resupply_rule_id:
            self.partner_resupply_rule_id.active = active

    def unlink(self):
        """
        This Method is override to archive all subcontracting field
        """
        for record in self:
            record._set_subcontracting_values_active(False)
        result = super(ResPartner, self).unlink()
        return result

    def write(self, values):
        for record in self:
            is_subcontractor_partner = values.get("is_subcontractor_partner")
            active = values.get("active")
            if is_subcontractor_partner is not None:
                values.update(record._update_subcontractor_entities_for_record(values))
            if active is not None:
                record._set_subcontracting_values_active(active)
        super(ResPartner, self).write(values)

    @api.model
    def create(self, values):
        partner = super(ResPartner, self).create(values)
        if values.get("is_subcontractor_partner", False):
            partner._create_subcontractor_entities()
        return partner

    def _compose_entity_name(self):
        """Compose entity name.
        Override this function to implement onw logic
        Returns:
            name (char) composed name
        """
        return self.display_name

    def _create_location(self, parent_location, company):
        """Creating Subcontracting Location starts here"""

        location_vals = {
            "name": self._compose_entity_name(),
            "usage": "internal",
            "location_id": parent_location or False,
            "company_id": company.id,
            "active": True,
        }
        location_rec = self.subcontracted_created_location_id
        if not location_rec:
            location_rec = self.env["stock.location"].create(location_vals)
        return location_rec

    def _create_subcontracted_operation_type(self, warehouse, location):
        """Creating Operation Type for Subcontracting"""
        name = self._compose_entity_name()
        operation_type_name = "{}: {}".format(name, " IN")
        sequence_code = ""
        for code in list(filter(None, operation_type_name.split(" "))):
            sequence_code += code[0]
        operation_type_rec = self.partner_picking_type_id
        if not operation_type_rec:
            operation_type_vals = {
                "name": operation_type_name,
                "code": "incoming",
                "sequence_code": sequence_code,
                "is_subcontractor": True,
            }
            if warehouse:
                operation_type_vals.update({"warehouse_id": warehouse.id})
            if location:
                operation_type_vals.update({"default_location_dest_id": location.id})
            operation_type_rec = self.env["stock.picking.type"].create(
                operation_type_vals
            )
        return operation_type_rec

    def _create_subcontracted_buy_rule(self, operation_type_rec, location):
        """Creating Route Rule for Subcontracting starts here"""
        rule = self.partner_buy_rule_id
        if not rule:
            buy_route = self.env.ref(
                "purchase_stock.route_warehouse0_buy", raise_if_not_found=False
            )
            rule = self.env["stock.rule"].create(
                {
                    "name": self._compose_entity_name(),
                    "action": "buy",
                    "picking_type_id": operation_type_rec.id,
                    "location_id": location.id,
                    "route_id": buy_route.id,
                }
            )
            self.partner_buy_rule_id = rule
        return rule

    def _create_subcontracted_resupply_rule(self, location):
        """# Creating Route Rule for Subcontracting resupply on order starts here"""
        resupply_on_order_route = self.env.ref(
            "mrp_subcontracting.route_resupply_subcontractor_mto",
            raise_if_not_found=False,
        )
        delivery_type = self.env.ref("stock.picking_type_out", raise_if_not_found=False)
        production = self.env["ir.property"]._get(
            "property_stock_production", "product.template"
        )
        pull_rule = self.partner_resupply_rule_id
        if not pull_rule:
            pull_rule = self.env["stock.rule"].create(
                {
                    "name": self._compose_entity_name(),
                    "action": "pull",
                    "partner_address_id": self._origin.id,
                    "picking_type_id": delivery_type.id,
                    "location_id": production.id,
                    "location_src_id": location.id,
                    "route_id": resupply_on_order_route.id,
                    "procure_method": "mts_else_mto",
                }
            )
            self.partner_resupply_rule_id = pull_rule
        return pull_rule

    def _create_subcontractor_entities(self):
        """Create entities for the subcontractor
        - Stock location
        - Stock operation type
        - "Buy" stock rule
        """
        for rec in self.filtered(lambda p: p.company_type == "company"):
            partner_update_vals = rec._create_subcontractor_entities_for_record()
            rec.write(partner_update_vals)

    def _update_subcontractor_entities_for_record(self, values):
        self.ensure_one()
        is_subcontractor_partner = values.get("is_subcontractor_partner")

        check_data = {
            # Updating Subcontracting Location
            "subcontracted_created_location_id": self._create_subcontracting_location_data,
            # Updating Subcontracting operation type
            "partner_picking_type_id": self._create_operation_type_for_subcontracting,
            # Updating Route Rule for Subcontracting buy
            "partner_buy_rule_id": self._create_route_rule_for_subcontracting,
            # Updating Route Rule for Subcontracting resupply
            "partner_resupply_rule_id": self._create_route_rule_for_subcontracting_resupply,
        }
        for field_name in check_data:
            if is_subcontractor_partner is True and getattr(self, field_name):
                getattr(self, field_name).active = True
            elif is_subcontractor_partner is True and not getattr(self, field_name):
                values.update(check_data[field_name]())
            elif is_subcontractor_partner is False and getattr(self, field_name):
                getattr(self, field_name).active = False

        return values

    def _create_subcontractor_entities_for_record(self):
        self.ensure_one()
        partner_update_vals = {"is_subcontractor_partner": True}
        # Creating Subcontracting Location ends here
        partner_update_vals.update(self._create_subcontracting_location_data())
        partner_update_vals.update(self._create_operation_type_for_subcontracting())
        # Creating Route Rule for Subcontracting starts here
        partner_update_vals.update(self._create_route_rule_for_subcontracting())
        # Creating Route Rule for Subcontracting resupply on order starts here
        partner_update_vals.update(
            self._create_route_rule_for_subcontracting_resupply()
        )
        return partner_update_vals

    def _get_location_for_record(self):
        self.ensure_one()
        location = self.subcontracted_created_location_id
        if not location:
            default_company = self.env.company
            company = self.company_id or default_company
            parent_location = (
                company.subcontracting_location_id
                and company.subcontracting_location_id.id
            )
            location = self._create_location(parent_location, company)
            self.subcontracted_created_location_id = location
        return location

    def _get_warehouse_for_record(self):
        self.ensure_one()
        default_company = self.env.company
        default_warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", default_company.id)]
        )[0]
        company = self.company_id or default_company
        warehouse = (
            self.env["stock.warehouse"].search([("company_id", "=", company.id)])[0]
            if self.company_id
            else default_warehouse
        )  # noqa
        return warehouse

    def _create_subcontracting_location_data(self):
        self.ensure_one()
        location = self._get_location_for_record()
        return {
            "property_stock_subcontractor": location.id,
            "subcontracted_created_location_id": location.id,
        }

    def _create_operation_type_for_subcontracting(self):
        self.ensure_one()
        operation_type_rec = self.partner_picking_type_id
        if not operation_type_rec:
            # Creating Operation Type for Subcontracting starts here
            location = self._get_location_for_record()
            warehouse = self._get_warehouse_for_record()
            operation_type_rec = self._create_subcontracted_operation_type(
                warehouse, location
            )
            self.partner_picking_type_id = operation_type_rec
        return {"partner_picking_type_id": operation_type_rec.id}

    def _create_route_rule_for_subcontracting(self):
        location = self._get_location_for_record()
        warehouse = self._get_warehouse_for_record()
        operation_type_rec = self._create_subcontracted_operation_type(
            warehouse, location
        )
        buy_rule = self._create_subcontracted_buy_rule(operation_type_rec, location)

        return {"partner_buy_rule_id": buy_rule.id}

    def _create_route_rule_for_subcontracting_resupply(self):
        location = self._get_location_for_record()
        resupply_rule = self._create_subcontracted_resupply_rule(location)
        return {"partner_resupply_rule_id": resupply_rule.id}
