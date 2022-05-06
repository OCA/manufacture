from odoo import api, fields, models

from ..constants import constants


class ResPartner(models.Model):
    _inherit = "res.partner"

    subcontractor_type = fields.Selection(
        string="Subcontractor type",
        help="""
            Subcontractor type can have the following values:
            - Buy
            - MTO+MTS
        """,
        selection=constants.SUBCONTRACTOR_TYPE_SELECTION,
    )
    partner_mts_mto_rule_id = fields.Many2one("stock.rule")

    def _set_subcontracting_values_active(self, active):
        self.ensure_one()
        if self.partner_mts_mto_rule_id:
            self.partner_mts_mto_rule_id.active = active
        return super(ResPartner, self)._set_subcontracting_values_active(active)

    def _create_subcontracted_mts_mto_rule(self, location):
        """# Creating MTS+MTO Route Rule for Subcontracting starts here"""
        first_name = self.name.split(" ")[0] or ""
        resupply_on_order_route = self.env.ref(
            "stock_mts_mto_rule.route_mto_mts",
        )
        delivery_type = self.env.ref("stock.picking_type_out", raise_if_not_found=False)
        production = self.env["ir.property"]._get(
            "property_stock_production", "product.template"
        )
        picking_type_id = self._create_operation_type_for_subcontracting()
        mts_rule_id = (
            self.env["stock.rule"]
            .search(
                [
                    ("location_src_id", "=", production.id),
                    "|",
                    ("active", "=", True),
                    ("active", "=", False),
                ],
                limit=1,
            )
            .id
        )
        if not mts_rule_id:
            mts_rule_id = (
                self.env["stock.rule"]
                .create(
                    {
                        "name": "Subcontractor mts pull from {}".format(first_name),
                        "action": "pull",
                        "picking_type_id": picking_type_id.get(
                            "partner_picking_type_id"
                        ),
                        "location_src_id": production.id,
                        "location_id": location.id,
                        "procure_method": "mts_else_mto",
                        "route_id": resupply_on_order_route.id,
                    }
                )
                .id
            )
        mto_rule_id = (
            self.env["stock.rule"]
            .search(
                [
                    ("location_src_id", "=", production.id),
                    "|",
                    ("active", "=", True),
                    ("active", "=", False),
                ],
                limit=1,
            )
            .id
        )
        if not mto_rule_id:
            mto_rule_id = (
                self.env["stock.rule"]
                .create(
                    {
                        "name": "Subcontractor mto pull from {}".format(first_name),
                        "action": "pull",
                        "picking_type_id": picking_type_id.get(
                            "partner_picking_type_id"
                        ),
                        "location_src_id": production.id,
                        "location_id": location.id,
                        "procure_method": "mts_else_mto",
                        "route_id": resupply_on_order_route.id,
                    }
                )
                .id
            )

        if not self.partner_mts_mto_rule_id:
            self.partner_mts_mto_rule_id = self.env["stock.rule"].create(
                {
                    "name": "Subcontractor {}".format(first_name),
                    "action": "split_procurement",
                    "partner_address_id": self._origin.id,
                    "mts_rule_id": mts_rule_id,
                    "mto_rule_id": mto_rule_id,
                    "picking_type_id": delivery_type.id,
                    "location_id": location.id,
                    "location_src_id": production.id,
                    "route_id": resupply_on_order_route.id,
                }
            )
        return self.partner_mts_mto_rule_id

    def _create_route_rule_for_subcontracting_mts_mto(self):
        location = self._get_location_for_record()
        mts_mto_rule = self._create_subcontracted_mts_mto_rule(location)
        return {"partner_mts_mto_rule_id": mts_mto_rule.id}

    def _update_subcontractor_entities_for_record(self, values):
        self.ensure_one()

        subcontractor_type = values.get("subcontractor_type", False)
        if not subcontractor_type:
            values.update(
                {
                    "is_subcontractor_partner": values.get(
                        "is_subcontractor_partner", False
                    ),
                }
            )
        else:
            values.update(
                {
                    "is_subcontractor_partner": True,
                }
            )

        check_data = {
            # Updating MTS+MTO Rule for Subcontracting resupply
            "partner_mts_mto_rule_id": self._create_route_rule_for_subcontracting_mts_mto,
        }
        need_mts_mto_rule = (
            subcontractor_type == constants.SUBCONTRACTOR_TYPE_SELECTION_BUY_MTS_MTO
        )
        for field_name in check_data:
            if need_mts_mto_rule is True and getattr(self, field_name):
                getattr(self, field_name).active = True
            elif need_mts_mto_rule is True and not getattr(self, field_name):
                values.update(check_data[field_name]())
            elif need_mts_mto_rule is False and getattr(self, field_name):
                getattr(self, field_name).active = False
        return super(ResPartner, self)._update_subcontractor_entities_for_record(values)

    def _create_subcontractor_entities_for_record(self):
        self.ensure_one()
        partner_update_vals = super(
            ResPartner, self
        )._create_subcontractor_entities_for_record()
        partner_update_vals.update(
            self._create_route_rule_for_subcontracting_mts_mto(),
        )
        partner_update_vals.update({"subcontractor_type": self.subcontractor_type})
        return partner_update_vals

    @api.model
    def create(self, values):
        subcontractor_type = values.get("subcontractor_type", False)
        if not subcontractor_type:
            values.update(
                {
                    "is_subcontractor_partner": values.get(
                        "is_subcontractor_partner", False
                    ),
                }
            )
        else:
            values.update(
                {
                    "is_subcontractor_partner": True,
                }
            )
        partner = super(ResPartner, self).create(values)
        return partner

    @api.onchange("subcontractor_type")
    def change_is_subcontractor_partner(self):
        if self.subcontractor_type:
            self.is_subcontractor_partner = True
        else:
            self.is_subcontractor_partner = False
