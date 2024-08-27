import re

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_subcontractor_partner = fields.Boolean(string="Subcontractor partner")
    subcontracted_created_location_id = fields.Many2one(
        comodel_name="stock.location", copy=False
    )
    partner_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type", copy=False
    )
    partner_buy_rule_id = fields.Many2one(comodel_name="stock.rule", copy=False)
    partner_resupply_rule_id = fields.Many2one(comodel_name="stock.rule", copy=False)

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

    def _set_subcontracting_values_active(self, active):
        """Set subcontracting values active/inactive by argument key"""
        for key in self.get_data_struct():
            self.mapped(key).write({"active": active})

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
        type_name = "%s:  IN" % name
        code = "".join(re.findall(r"\b\w", type_name))
        picks = partners.mapped("partner_picking_type_id")
        picks.write({"name": type_name, "sequence_code": code})

    def unlink(self):
        """This Method is override to archive all subcontracting field"""
        self._set_subcontracting_values_active(False)
        return super().unlink()

    def write(self, vals):
        if "is_subcontractor_partner" in vals:
            self._update_subcontractor_entities_for_record(
                vals.get("is_subcontractor_partner")
            )
        if "active" in vals:
            self._set_subcontracting_values_active(vals.get("active"))
        result = super().write(vals)
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
        return super().create(vals_list)

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
        picking_type_id, _ = self._create_subcontracted_operation_type(vals)
        return {"partner_picking_type_id": picking_type_id}

    def _create_route_rule_for_subcontracting(self, vals):
        picking_type_id, location_id = self._create_subcontracted_operation_type(vals)
        route = self.env.ref(
            "purchase_stock.route_warehouse0_buy", raise_if_not_found=False
        )
        buy_rule = self.env["stock.rule"].create(
            {
                "name": self._context.get("partner_name", self._compose_entity_name()),
                "action": "buy",
                "picking_type_id": picking_type_id,
                "location_dest_id": location_id,
                "route_id": route.id,
            }
        )
        return {"partner_buy_rule_id": buy_rule.id}

    def _create_route_rule_for_subcontracting_resupply(self, vals):
        prop = self.env["ir.property"]._get(
            "property_stock_production", "product.template"
        )
        company = self.company_id or self.env.company
        warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", company.id)], limit=1
        )
        picking_type = warehouse.out_type_id
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
                "location_dest_id": prop.id,
                "location_src_id": self._get_location_id_for_record(vals),
                "route_id": route.id,
                "procure_method": "mts_else_mto",
            }
        )
        return {"partner_resupply_rule_id": rule.id}
