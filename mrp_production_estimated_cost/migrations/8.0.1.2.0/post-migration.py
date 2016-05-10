# -*- coding: utf-8 -*-
# © 2016 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def update_manual_cost(cr):
    cr.execute(
        """
        UPDATE product_product
           SET manual_standard_cost = template.manual_standard_cost
           FROM product_template template
           WHERE template.id = product_product.product_tmpl_id;
        """)


def migrate(cr, version):
    if not version:
        return
    update_manual_cost(cr)
