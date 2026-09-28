# -*- coding: utf-8 -*-

from odoo import api, SUPERUSER_ID


def _post_init_hook(env):
    """Post initialization hook to handle PLM module integration."""
    try:
        # Check if mrp_plm module is installed and available
        # Use try-except to handle cases where the module might not be fully loaded yet
        try:
            plm_module = env['ir.module.module'].search([
                ('name', '=', 'mrp_plm'),
                ('state', '=', 'installed')
            ])
        except Exception:
            # If mrp_plm module is not available yet, skip the hook
            print("PLM module not available yet, skipping integration")
            return
        
        if plm_module:
            # Update database constraint for mrp_eco_bom_change table
            # Remove the NOT NULL constraint from product_id column
            env.cr.execute("""
                SELECT column_name, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'mrp_eco_bom_change' 
                AND column_name = 'product_id'
            """)
            result = env.cr.fetchone()
            
            if result and result[1] == 'NO':
                # The column has NOT NULL constraint, we need to remove it
                env.cr.execute("""
                    ALTER TABLE mrp_eco_bom_change 
                    ALTER COLUMN product_id DROP NOT NULL
                """)
                print("Removed NOT NULL constraint from mrp_eco_bom_change.product_id")
        else:
            print("PLM module not installed, skipping integration")
    except Exception as e:
        # Log any errors but don't fail the module installation
        print(f"Error in _post_init_hook: {e}")
        # Don't re-raise the exception to avoid blocking module installation


def _uninstall_hook(env):
    """Uninstallation hook to clean up PLM integration."""
    # Clean up any custom views or records created by this module
    # This is a placeholder for future cleanup if needed
    pass