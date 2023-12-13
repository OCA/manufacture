# Copyright 2023 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, fields, models


class Warehouse(models.Model):
    _inherit = "stock.warehouse"

    primecontractor_raw_material = fields.Boolean(
        "Primecontractor Raw Material",
        help="Define if the warehouse handles prime contractor raw material",
        default=False,
    )

    primecontractor_view_location_id = fields.Many2one(
        "stock.location",
        "Primecontractor Raw Material View Location",
        check_company=True,
    )
    wh_primecontractor_stock_loc_ids = fields.One2many(
        related="primecontractor_view_location_id.child_ids",
        string="Primecontractor Raw Material Locations",
    )
    primecontractor_pull_id = fields.Many2one("stock.rule", "Primecontractor Pull Rule")

    primecontractor_in_type_id = fields.Many2one(
        "stock.picking.type", "Primecontractor In Type"
    )

    def _get_locations_values(self, vals, code=False):
        res = super()._get_locations_values(vals, code)
        code = vals.get("code") or code or ""
        code = code.replace(" ", "").upper()
        company_id = vals.get(
            "company_id", self.default_get(["company_id"])["company_id"]
        )
        res.update(
            {
                "primecontractor_view_location_id": {
                    "name": "%s/PRM" % code,
                    "active": vals.get("primecontractor_raw_material", False),
                    "usage": "view",
                    "barcode": self._valid_barcode(code + "-PRM", company_id),
                }
            }
        )
        return res

    def _get_sequence_values(self):
        values = super()._get_sequence_values()
        values.update(
            {
                "primecontractor_in_type_id": {
                    "name": self.name + " " + _("Sequence Primecontractor"),
                    "prefix": self.code + "/PRM/",
                    "padding": 5,
                    "company_id": self.company_id.id,
                },
            }
        )
        return values

    def _get_picking_type_create_values(self, max_sequence):
        data, next_sequence = super()._get_picking_type_create_values(max_sequence)
        data.update(
            {
                "primecontractor_in_type_id": {
                    "name": _("Primecontractor"),
                    "code": "incoming",
                    "sequence": next_sequence,
                    "sequence_code": "PRM",
                    "warehouse_id": self.id,
                    "company_id": self.company_id.id,
                }
            }
        )
        return data, next_sequence + 1

    def _get_picking_type_update_values(self):
        data = super()._get_picking_type_update_values()
        data.update(
            {
                "primecontractor_in_type_id": {
                    "default_location_dest_id": self.primecontractor_view_location_id.id,
                    "barcode": self.code.replace(" ", "").upper() + "-PRM",
                },
            }
        )
        return data

    def _get_routes_values(self):
        routes = super()._get_routes_values()
        routes["reception_route_id"]["depends"].append("primecontractor_raw_material")
        return routes

    def _get_global_route_rules_values(self):
        rules = super()._get_global_route_rules_values()

        _, supplier_loc = self._get_partner_locations()

        if not self.primecontractor_in_type_id:
            # In case of a non initialized warehouse, picking type is not
            # automatically created:
            self.write(self._create_or_update_sequences_and_picking_types())

        rules.update(
            {
                "primecontractor_pull_id": {
                    "depends": ["primecontractor_raw_material"],
                    "create_values": {
                        "procure_method": "make_to_stock",
                        "company_id": self.company_id.id,
                        "action": "pull",
                        "auto": "manual",
                        "route_id": self.reception_route_id.id,
                        "location_id": self.primecontractor_view_location_id.id,
                        "location_src_id": supplier_loc.id,
                    },
                    "update_values": {
                        "name": self._format_rulename(
                            supplier_loc, self.primecontractor_view_location_id, ""
                        ),
                        "active": self.primecontractor_raw_material,
                        "picking_type_id": self.primecontractor_in_type_id.id,
                    },
                },
            }
        )
        return rules
