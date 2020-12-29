# © 2020 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json

from odoo.tests.common import SavepointCase


class TestRequest2Structure(SavepointCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        product = self.env.ref("mrp.product_product_wood_panel")
        self.bom = self.env.ref("mrp.mrp_bom_wood_panel")
        self.request = self.env["mrp.production.request"].create(
            {
                "name": "Test",
                "product_qty": 777.0,
                "product_id": product.id,
                "bom_id": self.bom.id,
            }
        )

    def test_generate_bom_structure_with_right_qty(self):
        action = self.request.with_context(uid=2).button_open_structure_report()
        param = self.env["ir.config_parameter"].get_param("request_bom_structure")
        param = json.loads(param)
        assert param == {"2": 777.0}
        res = (
            self.env["report.mrp.report_bom_structure"]
            .with_context(model="mrp.production.request", uid=2)
            .get_html(bom_id=self.bom.id)
        )
        assert res["bom_qty"] == 777.0
        return action
