# -*- coding: utf-8 -*-
# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

field_renames = [
    ('mrp.production.request', 'mrp_production_request', 'product_uom',
     'product_uom_id'),
]


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.rename_fields(env, field_renames)
