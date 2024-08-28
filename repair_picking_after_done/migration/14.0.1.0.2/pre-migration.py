# Copyright 2024 ForgeFlow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


def migrate(env, version):
    repairs = env["repair.order"].search([])
    for repair in repairs:
        repair.picking_ids.move_ids.write({"repair_id": repair.id})
