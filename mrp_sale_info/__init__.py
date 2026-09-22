# Copyright 2016 Antiun Ingenieria S.L. - Javier Iniesta
# Copyright 2019 Rubén Bravo <rubenred18@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from . import models


def mrp_sale_info_post_init_hook(env):
    """Post initialization hook for MRP Sale Info module.
    
    This hook is executed after module installation to automatically compute
    sale information for existing manufacturing orders and work orders.
    It ensures that pre-existing records are properly linked to sale information.
    
    Args:
        env: Odoo environment
    """
    # Get all manufacturing orders
    mrp_production_model = env['mrp.production']
    all_productions = mrp_production_model.search([])
    
    print(f"Starting sale information computation for {len(all_productions)} manufacturing orders...")
    
    # Process manufacturing orders in batches for better performance
    batch_size = 100
    for i in range(0, len(all_productions), batch_size):
        batch = all_productions[i:i + batch_size]
        
        # Find and set procurement groups for each batch
        for production in batch:
            # Check if source_procurement_group_id already exists
            if not production.source_procurement_group_id:
                # Strategy 1: Search through finished product move chain
                procurement_group = production.move_finished_ids.move_dest_ids.group_id[:1]
                
                # Strategy 2: If not found, search through raw material move chain
                if not procurement_group:
                    procurement_group = production.move_raw_ids.group_id[:1]
                
                if procurement_group:
                    # Set source_procurement_group_id
                    production.write({
                        'source_procurement_group_id': procurement_group.id
                    })
        
        # Force recomputation of sale-related fields for current batch
        batch._compute_sale_info()
        
        print(f"Processed batch {i//batch_size + 1}/{(len(all_productions)-1)//batch_size + 1}")
    
    print(f"Manufacturing order data migration completed. Processed {len(all_productions)} orders")
    
    # Also process work order data
    mrp_workorder_model = env['mrp.workorder']
    all_workorders = mrp_workorder_model.search([])
    
    print(f"Starting sale information computation for {len(all_workorders)} work orders...")
    
    # Process work orders in batches
    for i in range(0, len(all_workorders), batch_size):
        batch = all_workorders[i:i + batch_size]
        # Force recomputation of sale-related fields for work orders
        batch._compute_sale_info()
        
        print(f"Processed work order batch {i//batch_size + 1}/{(len(all_workorders)-1)//batch_size + 1}")
    
    print(f"Work order data migration completed. Processed {len(all_workorders)} work orders")
    print("Data migration completed successfully!")