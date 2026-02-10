# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
# Copyright 2019 Odoo
# Copyright 2020 Tecnativa - Alexandre Díaz
# Copyright 2020 Tecnativa - Pedro M. Baeza

from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for warehouse in env["stock.warehouse"].search([]):
        warehouse.write({"subcontracting_to_resupply": True})


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    warehouses = env["stock.warehouse"].search([])
    subcontracting_routes = warehouses.mapped("subcontracting_route_id")
    warehouses.write({"subcontracting_route_id": False})
    # Fail unlink means that the route is used somewhere (e.g. route_id on
    # procurement.rule). In this case, we don't try to do anything.
    try:
        subcontracting_routes.unlink()
    except Exception:
        pass
