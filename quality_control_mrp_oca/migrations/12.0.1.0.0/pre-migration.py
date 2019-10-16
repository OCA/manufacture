from openupgradelib import openupgrade

field_renames = [
    ("mrp.production", "mrp_production", "qc_inspections",
     "qc_inspections_ids"),
    ("qc.inspection", "qc_inspection", "production", "production_id"),
    ("qc.inspection.line", "qc_inspection_line", "production", "production_id")
]


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.rename_fields(env, field_renames)
