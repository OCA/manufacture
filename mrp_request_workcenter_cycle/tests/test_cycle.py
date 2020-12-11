# copyright 2020 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import SavepointCase


class TestMrpRequestCycle(SavepointCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

    def test_pool_of_mo(self):
        product = self.env.ref("mrp.product_product_wood_panel")
        request = self.env["mrp.production.request"].create(
            {
                "product_id": product.id,
                "bom_id": self.env["mrp.bom"]
                .search([("product_tmpl_id", "=", product.product_tmpl_id.id)], limit=1)
                .id,
                "name": "test",
            }
        )
        request.populate_qty_by_workcenter()
        assert request.auto_product_qty == 270
        assert request.product_qty == 270
        request.button_to_approve()
        request.button_approved()
        request.button_create_mo_by_workcenter()
        assert request.mrp_production_count == 3
        qties = [x.product_qty for x in request.mrp_production_ids]
        qties.sort()
        assert qties == [80, 80, 110]
