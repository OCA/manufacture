# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_field_renames = [
    ('qc.trigger', 'qc_trigger', 'picking_type', 'picking_type_id'),
    ('qc.inspection', 'qc_inspection', 'picking', 'picking_id'),
    ('qc.inspection', 'qc_inspection', 'lot', 'lot_id'),
    ('qc.inspection.line', 'qc_inspection_line', 'picking', 'picking_id'),
    ('qc.inspection.line', 'qc_inspection_line', 'lot', 'lot_id'),
    ('stock.picking', 'stock_picking', 'qc_inspections', 'qc_inspections_ids'),
    ('stock.production.lot', 'stock_production_lot', 'qc_inspections',
     'qc_inspections_ids'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
