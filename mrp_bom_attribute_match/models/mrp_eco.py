from odoo import models, fields, api, Command
from collections import defaultdict
from odoo.tools import float_compare


class MrpEco(models.Model):
    _inherit = 'mrp.eco'

    def _get_difference_bom_lines(self, old_bom, new_bom):
        """Override PLM module's method to include component_template_id field"""
        # Return difference lines from two bill of material.
        def bom_line_key(line):
            return (
                line.product_id, line.operation_id._get_comparison_values(),
                tuple(line.bom_product_template_attribute_value_ids.ids),
            )
        new_bom_commands = [(5,)]
        old_bom_lines = list(old_bom.bom_line_ids)
        if self.new_bom_id:
            for line in new_bom.bom_line_ids:
                old_line = False
                for i, bom_line in enumerate(old_bom_lines):
                    if bom_line_key(line) == bom_line_key(bom_line):
                        old_line = old_bom_lines.pop(i)
                        break
                if old_line and (line.product_uom_id != old_line.product_uom_id or
                   float_compare(line.product_qty, old_line.product_qty, precision_rounding=line.product_uom_id.rounding)):
                    change_vals = {
                        'change_type': 'update',
                        'product_id': line.product_id.id,
                        'old_uom_id': old_line.product_uom_id.id,
                        'new_uom_id': line.product_uom_id.id,
                        'old_operation_id': old_line.operation_id.id,
                        'new_operation_id': line.operation_id.id,
                        'new_product_qty': line.product_qty,
                        'old_product_qty': old_line.product_qty
                    }
                    # Include component_template_id if it exists in the line
                    if hasattr(line, 'component_template_id') and line.component_template_id:
                        change_vals['component_template_id'] = line.component_template_id.id
                    new_bom_commands += [Command.create(change_vals)]
                elif not old_line:
                    change_vals = {
                        'change_type': 'add',
                        'product_id': line.product_id.id,
                        'new_uom_id': line.product_uom_id.id,
                        'new_operation_id': line.operation_id.id,
                        'new_product_qty': line.product_qty
                    }
                    # Include component_template_id if it exists in the line
                    if hasattr(line, 'component_template_id') and line.component_template_id:
                        change_vals['component_template_id'] = line.component_template_id.id
                    new_bom_commands += [Command.create(change_vals)]
            for old_line in old_bom_lines:
                change_vals = {
                    'change_type': 'remove',
                    'product_id': old_line.product_id.id,
                    'old_uom_id': old_line.product_uom_id.id,
                    'old_operation_id': old_line.operation_id.id,
                    'old_product_qty': old_line.product_qty,
                }
                # Include component_template_id if it exists in the line
                if hasattr(old_line, 'component_template_id') and old_line.component_template_id:
                    change_vals['component_template_id'] = old_line.component_template_id.id
                new_bom_commands += [Command.create(change_vals)]
        return new_bom_commands