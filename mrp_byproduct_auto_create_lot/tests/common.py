# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


class CommonMrpByproductAutoCreateLot:
    def assertUniqueIn(self, element_list):
        elements = []
        for element in element_list:
            if element in elements:
                raise Exception(f"Element {element} is not unique in list")
            elements.append(element)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
                skip_bom_alignment_check=True,
            )
        )
        cls.lot_obj = cls.env["stock.lot"]
        cls.manufacture_route = cls.env.ref("mrp.route_warehouse0_manufacture")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.supplier = cls.env["res.partner"].create({"name": "Supplier - test"})

        cls.product_manuf = cls.env["product.product"].create(
            {
                "name": "Manuf",
                "type": "consu",
                "uom_id": cls.uom_unit.id,
                "route_ids": [(6, 0, cls.manufacture_route.ids)],
            }
        )

    @classmethod
    def _create_product(cls, tracking="lot", auto=True):
        name = f"{tracking} - {auto}"
        return cls.env["product.product"].create(
            {
                "name": name,
                "type": "consu",
                "tracking": tracking,
                "auto_create_lot": auto,
                "is_storable": True,
            }
        )

    @classmethod
    def _create_bom(cls, product=None, by_product=None):
        bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product_manuf.product_tmpl_id.id,
                "type": "normal",
                "byproduct_ids": [
                    (0, 0, {"product_id": by_product.id, "product_qty": 1.0})
                ],
            }
        )
        return bom

    @classmethod
    def _create_manufacturing_order(cls, bom=None, by_product_qty=1.0):
        cls.mo = cls.env["mrp.production"].create(
            {
                "product_id": cls.product_manuf.id,
                "product_qty": 1.0,
                "bom_id": bom.id if bom else cls.bom.id,
                "move_byproduct_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": bom.byproduct_ids[0].product_id.id
                            if bom
                            else cls.bom.byproduct_ids[0].product_id.id,
                            "product_uom_qty": by_product_qty,
                        },
                    )
                ],
            }
        )
        return cls.mo
