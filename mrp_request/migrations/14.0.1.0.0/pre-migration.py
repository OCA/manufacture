# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_field_renames = [
    ("mrp.production", "mrp_production", "mrp_production_request_id", "mrp_request_id"),
    (
        "product.template",
        "product_template",
        "mrp_production_request",
        "mrp_request",
    ),
    (
        "stock.move",
        "stock_move",
        "created_mrp_production_request_id",
        "created_mrp_request_id",
    ),
    (
        "mrp.request.create.mo",
        "mrp_request_create_mo",
        "mrp_production_request_id",
        "mrp_request_id",
    ),
    (
        "mrp.production.request.create.mo.line",
        "mrp_production_request_create_mo_line",
        "mrp_production_request_create_mo_id",
        "mrp_request_create_mo_id",
    ),
]

_model_renames = [
    ("mrp.production.request", "mrp.request"),
    ("mrp.production.request.create.mo", "mrp.request.create.mo"),
    ("mrp.production.request.create.mo.line", "mrp.request.create.mo.line"),
]

_table_renames = [
    ("mrp_production_request", "mrp_request"),
    ("mrp_production_request_create_mo", "mrp_request_create_mo"),
    ("mrp_production_request_create_mo_line", "mrp_request_create_mo_line"),
]

_xmlid_renames = [
    (
        "mrp_request.seq_mrp_production_request",
        "mrp_request.seq_mrp_request",
    ),
    (
        "mrp_request.access_mrp_production_request_user",
        "mrp_request.access_mrp_request_user",
    ),
    (
        "mrp_request.access_mrp_production_request_manager",
        "mrp_request.access_mrp_request_manager",
    ),
    (
        "mrp_request.module_category_mrp_production_request",
        "mrp_request.module_category_mrp_request",
    ),
    (
        "mrp_request.group_mrp_production_request_user",
        "mrp_request.group_mrp_request_user",
    ),
    (
        "mrp_request.group_mrp_production_request_manager",
        "mrp_request.group_mrp_request_manager",
    ),
    (
        "mrp_request.mrp_production_request_comp_rule",
        "mrp_request.mrp_request_comp_rule",
    ),
    (
        "mrp_request.mrp_production_request_followers_rule",
        "mrp_request.mrp_request_followers_rule",
    ),
    (
        "mrp_request.mrp_production_request_rule",
        "mrp_request.mrp_request_rule",
    ),
    (
        "mrp_request.view_mrp_production_request_form",
        "mrp_request.view_mrp_request_form",
    ),
    (
        "mrp_request.view_mrp_production_request_tree",
        "mrp_request.view_mrp_request_tree",
    ),
    (
        "mrp_request.view_mrp_production_request_search",
        "mrp_request.view_mrp_request_search",
    ),
    (
        "mrp_request.mrp_production_request_action",
        "mrp_request.mrp_request_action",
    ),
    (
        "mrp_request.menu_mrp_production_request_act",
        "mrp_request.menu_mrp_request_act",
    ),
    (
        "mrp_request.action_server_mrp_production_request_refresh",
        "mrp_request.action_server_mrp_request_refresh",
    ),
    (
        "mrp_request.mrp_production_request_create_mo_view",
        "mrp_request.mrp_request_create_mo_view",
    ),
    (
        "mrp_request.mrp_production_request_create_mo_action",
        "mrp_request.mrp_request_create_mo_action",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_models(cr, _model_renames)
    openupgrade.rename_tables(cr, _table_renames)
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_xmlids(cr, _xmlid_renames)
    env.ref("mrp_request.seq_mrp_request").write(
        {
            "code": "mrp.request",
        }
    )
