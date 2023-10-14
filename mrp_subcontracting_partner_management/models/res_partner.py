from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_subcontractor_partner = fields.Boolean(string="Subcontractor")
    subcontracted_created_location_id = fields.Many2one(
        comodel_name="stock.location", copy=False
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
            # Updating Route Rule for Subcontracting buy
            "partner_buy_rule_id": "_create_route_rule_for_subcontracting",
            # Updating Route Rule for Subcontracting resupply
            "partner_resupply_rule_id": "_create_route_rule_for_subcontracting_resupply",
        }

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
        for field in field_names:
            records = partners.mapped(field)
            records.write({"name": name})
            self._update_name_translation(records, name)

    def unlink(self):
        """This Method is override to archive all subcontracting field"""
        self._set_subcontracting_values_active(False)
        return super(ResPartner, self).unlink()

    def write(self, vals):
        if "is_subcontractor_partner" in vals:
            self._update_subcontractor_entities_for_record(
                vals.get("is_subcontractor_partner")
            )
        if "active" in vals:
            self._set_subcontracting_values_active(vals.get("active"))
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
        partners = super(ResPartner, self).create(vals_list)
        for partner in partners.filtered(
            lambda p: p.is_subcontractor_partner and p.is_company
        ):
            partner.partner_resupply_rule_id.write({"partner_address_id": partner.id})
        return partners

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

    def _create_route_rule_for_subcontracting(self, vals):
        # operation_type_rec_id, location_id = self._create_subcontracted_operation_type(
        #     vals
        # )
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
