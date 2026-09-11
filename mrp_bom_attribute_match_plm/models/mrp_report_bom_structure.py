# -*- coding: utf-8 -*-

from odoo import models


class ReportBomStructure(models.AbstractModel):
    """Extend PLM BOM report structure to support component_template_id"""
    
    _inherit = 'report.mrp.report_bom_structure'

    def _get_bom_data(self, bom, warehouse, product=False, line_qty=False, bom_line=False, level=0, parent_bom=False, parent_product=False, index=0, product_info=False, ignore_stock=False):
        """Override to handle component_template_id in BOM data"""
        res = super()._get_bom_data(bom, warehouse, product, line_qty, bom_line, level, parent_bom, parent_product, index, product_info, ignore_stock)
        
        # Add component_template_id support for PLM users
        if self.env.user.user_has_groups('mrp_plm.group_plm_user'):
            # Check if this is a BOM line with component_template_id
            if bom_line and hasattr(bom_line, 'component_template_id') and bom_line.component_template_id:
                res['component_template_id'] = bom_line.component_template_id.id
                res['component_template_name'] = bom_line.component_template_id.display_name
                
                # If product_id is not set but component_template_id is set,
                # we need to handle the dynamic component logic
                if not res.get('product_id') and bom_line.component_template_id:
                    # Use the component template's default product variant
                    default_product = bom_line.component_template_id.product_variant_ids[:1]
                    if default_product:
                        res['product_id'] = default_product.id
                        res['product_name'] = default_product.display_name
        
        return res

    def _get_component_data(self, parent_bom, parent_product, warehouse, bom_line, line_quantity, level, index, product_info, ignore_stock=False):
        """Override to handle component_template_id in component data"""
        res = super()._get_component_data(parent_bom, parent_product, warehouse, bom_line, line_quantity, level, index, product_info, ignore_stock)
        
        # Add component_template_id support for PLM users
        if self.env.user.user_has_groups('mrp_plm.group_plm_user'):
            # Check if this is a BOM line with component_template_id
            if bom_line and hasattr(bom_line, 'component_template_id') and bom_line.component_template_id:
                res['component_template_id'] = bom_line.component_template_id.id
                res['component_template_name'] = bom_line.component_template_id.display_name
                
                # If product_id is not set but component_template_id is set,
                # we need to handle the dynamic component logic
                if not res.get('product_id') and bom_line.component_template_id:
                    # Use the component template's default product variant
                    default_product = bom_line.component_template_id.product_variant_ids[:1]
                    if default_product:
                        res['product_id'] = default_product.id
                        res['product_name'] = default_product.display_name
                        res['product_code'] = default_product.default_code or ''
        
        return res

    def _get_bom_array_lines(self, data, level, unfolded_ids, unfolded, parent_unfolded):
        """Override to include component_template_id in BOM array lines"""
        lines = super()._get_bom_array_lines(data, level, unfolded_ids, unfolded, parent_unfolded)
        
        # Add component_template_id support for PLM users
        if self.env.user.user_has_groups('mrp_plm.group_plm_user'):
            for line in lines:
                # Check if this line has component_template_id data
                if 'component_template_id' in data:
                    line['component_template_id'] = data['component_template_id']
                    line['component_template_name'] = data.get('component_template_name', '')
        
        return lines