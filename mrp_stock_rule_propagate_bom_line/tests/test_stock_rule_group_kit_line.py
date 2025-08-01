# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields
from odoo.tests import Form, SavepointCase


class TestStockMoveBomLinePropagate(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.partner = cls.env["res.partner"].create({"name": "customer"})

        # Set WH for multi step delivery
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.delivery_steps = "pick_pack_ship"

        # Set "WH: Output → Customers" to propagate BOM line
        for rule in cls.warehouse.delivery_route_id.rule_ids:
            if rule.location_src_id == cls.warehouse.wh_output_stock_loc_id:
                rule.propagate_bom_line = True

        # Create products and BOMs
        cls.kit_product_1 = cls._create_product("kit product 1")
        cls.kit_product_2 = cls._create_product("kit product 2")
        cls.component_product_1 = cls._create_product("component product 1")
        cls.component_product_2 = cls._create_product("component product 2")
        cls.component_product_3 = cls._create_product("component product 3")

        cls._create_kit_bom(
            cls.kit_product_1,
            [
                {"product_id": cls.component_product_1, "qty": 2.0},
                {"product_id": cls.component_product_2, "qty": 2.0},
            ],
        )
        cls._create_kit_bom(
            cls.kit_product_2,
            [
                {"product_id": cls.component_product_1, "qty": 2.0},
                {"product_id": cls.component_product_3, "qty": 2.0},
            ],
        )

    @classmethod
    def _create_product(cls, name):
        product_form = Form(cls.env["product.product"])
        product_form.name = name
        return product_form.save()

    @classmethod
    def _create_kit_bom(cls, kit_product, bom_line_specs):
        bom_form = Form(cls.env["mrp.bom"])
        bom_form.product_tmpl_id = kit_product.product_tmpl_id
        bom_form.type = "phantom"
        for bom_line_spec in bom_line_specs:
            with bom_form.bom_line_ids.new() as bom_line_form:
                bom_line_form.product_id = bom_line_spec["product_id"]
                bom_line_form.product_qty = bom_line_spec["qty"]
        return bom_form.save()

    @classmethod
    def _procure_for_delivery(cls, product_qty_tuple_list):
        procurement_group = cls.env["procurement.group"].create({"name": "Test"})
        procurements = []
        for product, qty in product_qty_tuple_list:
            procurements.append(
                cls.env["procurement.group"].Procurement(
                    product,
                    qty,
                    product.uom_id,
                    cls.partner.property_stock_customer,
                    product.display_name,
                    "TEST",
                    cls.warehouse.company_id,
                    {
                        "group_id": procurement_group,
                        "date_planned": fields.Datetime.now(),
                        "date_deadline": fields.Datetime.now(),
                        "route_ids": cls.env["stock.location.route"].browse(),
                        "warehouse_id": cls.warehouse or False,
                        "partner_id": cls.partner.id,
                        "product_description_variants": "",
                        "company_id": cls.warehouse.company_id,
                    },
                )
            )
        cls.env["procurement.group"].run(procurements)

    def test_delivery_propagate_bom_line(self):
        self._procure_for_delivery(
            [(self.kit_product_1, 2.0), (self.kit_product_2, 2.0)]
        )
        delivery_order = self.env["stock.picking"].search(
            [("picking_type_code", "=", "outgoing")], order="id desc", limit=1
        )
        self.assertEqual(len(delivery_order.move_lines), 4)
        # Since the flag is set on "WH: Output → Customers", the moves generated
        #  from Packing zone to Output are not grouped
        pack_order = delivery_order.move_lines.move_orig_ids.picking_id
        self.assertEqual(len(pack_order.move_lines), 4)
        # Since the flag is not set on "WH: Packing zone → Output", the moves generated
        #  from Stock to Packing zone are grouped
        pick_order = pack_order.move_lines.move_orig_ids.picking_id
        self.assertEqual(len(pick_order.move_lines), 3)
