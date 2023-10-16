# Copyright 2023 ForgeFlow S.L. (https://forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    products = env["product.product"].search([])
    for product in products:
        mrp_product_llc = env["mrp.product.llc"].create(
            {
                "product_id": product.id,
                "llc": 0,
            }
        )
        product.write({"mrp_product_llc_id": mrp_product_llc.id})

