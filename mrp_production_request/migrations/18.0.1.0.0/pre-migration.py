from openupgradelib import openupgrade

_field_renames = [
    (
        "mrp.production.request",
        "mrp_production_request",
        "date_planned_start",
        "date_start",
    ),
    (
        "mrp.production.request",
        "mrp_production_request",
        "date_planned_finished",
        "date_finished",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
