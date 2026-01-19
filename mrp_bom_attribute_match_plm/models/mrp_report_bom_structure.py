# -*- coding: utf-8 -*-

from odoo import models, api


class ReportBomStructure(models.AbstractModel):
    """Extend PLM BOM report structure to support component_template_id and handle BOM preview permissions"""
    
    _inherit = 'report.mrp.report_bom_structure'

    def _get_bom_data(self, bom, warehouse, product=False, line_qty=False, bom_line=False, level=0, parent_bom=False, parent_product=False, index=0, product_info=False, ignore_stock=False):
        """Override to handle component_template_id in BOM data and BOM preview permissions"""
        # Check if user is in "Manufacturing/User" group and needs permission bypass for BOM preview
        user = self.env.user
        if user.user_has_groups('mrp.group_mrp_user') and not user.user_has_groups('mrp.group_mrp_manager'):
            # Manufacturing/User group without Manager permissions - use sudo for BOM line access
            bom = bom.sudo()
            if product:
                product = product.sudo()
        
        # Call the original method with potentially sudo-ized objects
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
        """Override to handle component_template_id in component data and BOM preview permissions"""
        # Check if user is in "Manufacturing/User" group and needs permission bypass for BOM preview
        user = self.env.user
        if user.user_has_groups('mrp.group_mrp_user') and not user.user_has_groups('mrp.group_mrp_manager'):
            # Manufacturing/User group without Manager permissions - use sudo for BOM line access
            parent_bom = parent_bom.sudo()
            if parent_product:
                parent_product = parent_product.sudo()
            bom_line = bom_line.sudo()
        
        # Call the original method with potentially sudo-ized objects
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

    def get_html(self, bom_id=False, searchQty=1, searchVariant=False):
        """Override to handle BOM preview permissions for Manufacturing/User group"""
        user = self.env.user
        if user.user_has_groups('mrp.group_mrp_user') and not user.user_has_groups('mrp.group_mrp_manager'):
            # Manufacturing/User group without Manager permissions - use sudo for HTML generation
            # Use sudo when browsing BOM to avoid permission issues
            bom_id = bom_id or self.env.context.get('active_id')
            if bom_id:
                bom = self.env['mrp.bom'].sudo().browse(bom_id)
            else:
                bom = self.env['mrp.bom'].sudo()
            
            # Also use sudo for product browsing if searchVariant is provided
            if searchVariant:
                product = self.env['product.product'].sudo().browse(int(searchVariant))
            else:
                product = self.env['product.product'].sudo()
            
            # Call the original method with sudo context
            return super(ReportBomStructure, self.sudo()).get_html(bom_id, searchQty, searchVariant)
        else:
            # Normal users or managers - use regular permissions
            return super().get_html(bom_id, searchQty, searchVariant)

    def _get_report_data(self, bom_id=False, searchQty=1, searchVariant=False):
        """Override to handle BOM preview permissions for Manufacturing/User group"""
        user = self.env.user
        if user.user_has_groups('mrp.group_mrp_user') and not user.user_has_groups('mrp.group_mrp_manager'):
            # Manufacturing/User group without Manager permissions - use sudo for report data
            # Use sudo when browsing BOM to avoid permission issues
            bom_id = bom_id or self.env.context.get('active_id')
            if bom_id:
                bom = self.env['mrp.bom'].sudo().browse(bom_id)
            else:
                bom = self.env['mrp.bom'].sudo()
            
            # Also use sudo for product browsing if searchVariant is provided
            if searchVariant:
                product = self.env['product.product'].sudo().browse(int(searchVariant))
            else:
                product = self.env['product.product'].sudo()
            
            # Call the original method with sudo context
            return super(ReportBomStructure, self.sudo())._get_report_data(bom_id, searchQty, searchVariant)
        else:
            # Normal users or managers - use regular permissions
            return super()._get_report_data(bom_id, searchQty, searchVariant)