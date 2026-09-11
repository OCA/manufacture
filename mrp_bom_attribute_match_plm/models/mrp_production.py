from odoo import models, api, _
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _link_bom(self, bom):
        """
        Override the _link_bom method to bypass BOM write access checks
        for manufacturing users during MO creation.
        """
        # Check if the current user is in mrp.group_mrp_user (manufacturing user)
        # and doesn't have write access to BOM
        user_has_bom_write_access = self.env.user.has_group('mrp.group_mrp_user') and \
            self.env['mrp.bom'].check_access_rights('write', raise_exception=False)
        
        # If user is manufacturing user without BOM write access, use sudo for BOM operations
        if self.env.user.has_group('mrp.group_mrp_user') and not user_has_bom_write_access:
            # Use sudo to bypass access rights for BOM operations
            return super(MrpProduction, self.sudo())._link_bom(bom)
        
        # Otherwise, use the standard method
        return super()._link_bom(bom)

    @api.model
    def create(self, vals):
        """
        Override create method to handle BOM assignment for manufacturing users
        without BOM write permissions.
        """
        # Check if bom_id is provided and user is manufacturing user without BOM write access
        bom_id = vals.get('bom_id')
        user_has_bom_write_access = self.env.user.has_group('mrp.group_mrp_user') and \
            self.env['mrp.bom'].check_access_rights('write', raise_exception=False)
        
        if bom_id and self.env.user.has_group('mrp.group_mrp_user') and not user_has_bom_write_access:
            # Create the MO first without bom_id to avoid access error
            bom = self.env['mrp.bom'].browse(bom_id)
            if not bom.exists():
                raise UserError(_("The selected BOM does not exist."))
            
            # Remove bom_id from vals temporarily
            vals_without_bom = vals.copy()
            vals_without_bom.pop('bom_id', None)
            
            # Create MO without bom_id
            mo = super(MrpProduction, self).create(vals_without_bom)
            
            # Use sudo to assign bom_id
            mo.sudo().write({'bom_id': bom_id})
            
            # Call _link_bom using sudo to bypass access checks
            mo.sudo()._link_bom(bom)
            
            return mo
        
        # Standard creation process
        return super().create(vals)