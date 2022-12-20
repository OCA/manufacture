# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import SUPERUSER_ID, api, tools


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    all_workorders = env["mrp.workorder"].search([], order="production_id ASC, id ASC")
    for _, workorders in tools.groupby(all_workorders, lambda w: w.production_id):
        for seq, wo in enumerate(workorders, 1):
            wo.sequence = seq
