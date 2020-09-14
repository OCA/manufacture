# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class ProductProduct(models.Model):

    _inherit = "product.product"

    def name_get(self):
        res = super().name_get()
        if not self.env.context.get("unbuild_rebuild"):
            return res
        updated_names = []
        for product_id, name in res:
            product = self.browse(product_id)
            attributes_string = ", ".join([a.name for a in product.attribute_value_ids])
            if attributes_string:
                updated_name = "{} - {}".format(name, attributes_string)
                updated_names.append((product_id, updated_name))
                continue
            updated_names.append((product_id, name))
        return updated_names
