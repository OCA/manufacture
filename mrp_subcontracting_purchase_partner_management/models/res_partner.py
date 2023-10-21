from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def get_data_struct(self):
        result = super(ResPartner, self).get_data_struct()
        # Remove preparing `partner_picking_type_id` field value
        result.pop("partner_picking_type_id", False)
        return result

    def _update_subcontractor_values_name(self, name):
        # Update values without functional dependencies on partner_picking_type_id field
        partners = self.filtered(lambda p: p.is_subcontractor_partner)
        field_names = [*self.get_data_struct(), "property_stock_subcontractor"]
        for field in field_names:
            records = partners.mapped(field)
            records.write({"name": name})
            self._update_name_translation(records, name)

    @api.model_create_multi
    def create(self, vals_list):
        partners = super(ResPartner, self).create(vals_list)
        for partner in partners.filtered(
            lambda p: p.is_subcontractor_partner and p.is_company
        ):
            partner.partner_resupply_rule_id.write({"partner_address_id": partner.id})
        return partners

    def _create_route_rule_for_subcontracting(self, vals):
        # Overide this function
        location_id = self._get_location_id_for_record(vals)
        picking_type_id = (
            self.env["stock.picking.type"]
            .with_context(active_test=False)
            .search(
                [
                    ("name", "=", "Dropship"),
                    ("sequence_code", "=", "DS"),
                    ("company_id", "=", self.env.company.id),
                ],
                limit=1,
            )
            .id
        )
        route = self.env.ref(
            "mrp_subcontracting_purchase.route_subcontracting_dropshipping",
            raise_if_not_found=False,
        )
        buy_rule = self.env["stock.rule"].create(
            {
                "name": "Vendors → %s"
                % self._context.get("partner_name", self._compose_entity_name()),
                "action": "buy",
                "location_id": location_id,
                "route_id": route.id,
                "picking_type_id": picking_type_id,
            }
        )
        return {"partner_buy_rule_id": buy_rule.id}

    def _create_route_rule_for_subcontracting_resupply(self, vals):
        prop = self.env["ir.property"]._get(
            "property_stock_production", "product.template"
        )
        route = self.env.ref(
            "mrp_subcontracting_purchase.route_subcontracting_dropshipping",
            raise_if_not_found=False,
        )
        picking_type_id = (
            self.env["stock.picking.type"]
            .with_context(active_test=False)
            .search(
                [("name", "=", "Subcontracting"), ("sequence_code", "=", "SBC")],
                limit=1,
            )
            .id
        )
        rule = self.env["stock.rule"].create(
            {
                "name": "%s - Production"
                % self._context.get("partner_name", self._compose_entity_name()),
                "action": "pull",
                "picking_type_id": picking_type_id,
                "location_src_id": self._get_location_id_for_record(vals),
                "location_id": prop.id,
                "route_id": route.id,
                "partner_address_id": self._origin.id,
                "procure_method": "make_to_order",
            }
        )
        return {"partner_resupply_rule_id": rule.id}
