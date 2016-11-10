# -*- coding: utf-8 -*-
# (c) 2016 Esther Martín - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def migrate(cr, version):
    if not version:
        return
    cr.execute("""
        UPDATE mrp_operation_workcenter
        SET
            capacity_per_cycle = mw.capacity_per_cycle,
            time_cycle = mw.time_cycle,
            time_start = mw.time_start,
            time_efficiency = rr.time_efficiency,
            time_stop = mw.time_stop,
            op_number = mw.op_number,
            op_avg_cost = mw.op_avg_cost
        FROM mrp_workcenter mw, resource_resource rr
        WHERE mrp_operation_workcenter.workcenter = mw.id and
        mrp_operation_workcenter.custom_data = False and
        rr.id = mw.resource_id;
        """)
