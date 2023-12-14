
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/manufacture&target_branch=13.0)
[![Pre-commit Status](https://github.com/OCA/manufacture/actions/workflows/pre-commit.yml/badge.svg?branch=13.0)](https://github.com/OCA/manufacture/actions/workflows/pre-commit.yml?query=branch%3A13.0)
[![Build Status](https://github.com/OCA/manufacture/actions/workflows/test.yml/badge.svg?branch=13.0)](https://github.com/OCA/manufacture/actions/workflows/test.yml?query=branch%3A13.0)
[![codecov](https://codecov.io/gh/OCA/manufacture/branch/13.0/graph/badge.svg)](https://codecov.io/gh/OCA/manufacture)
[![Translation Status](https://translation.odoo-community.org/widgets/manufacture-13-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/manufacture-13-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# Odoo Manufacturing Modules

Odoo modules related to Manufacturing

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[account_move_line_manufacture_info](account_move_line_manufacture_info/) | 13.0.1.0.0 |  | Account Move Line Manufacture Information
[base_repair](base_repair/) | 13.0.1.1.0 | [![marcelsavegnago](https://github.com/marcelsavegnago.png?size=30px)](https://github.com/marcelsavegnago) | This module extends the functionality of Odoo Repair module to add some basic features.
[base_repair_config](base_repair_config/) | 13.0.1.0.0 | [![marcelsavegnago](https://github.com/marcelsavegnago.png?size=30px)](https://github.com/marcelsavegnago) | Provides general settings for the Maintenance App
[mrp_bom_component_menu](mrp_bom_component_menu/) | 13.0.1.0.0 |  | MRP BOM Component Menu
[mrp_bom_line_sequence](mrp_bom_line_sequence/) | 13.0.1.0.0 |  | Manages the order of BOM lines by displaying its sequence
[mrp_bom_location](mrp_bom_location/) | 13.0.1.0.1 |  | Adds location field to Bill of Materials and its components.
[mrp_bom_note](mrp_bom_note/) | 13.0.1.0.0 |  | Notes in Bill of Materials
[mrp_bom_tracking](mrp_bom_tracking/) | 13.0.1.0.1 |  | Logs any change to a BoM in the chatter
[mrp_multi_level](mrp_multi_level/) | 13.0.1.15.3 | [![JordiBForgeFlow](https://github.com/JordiBForgeFlow.png?size=30px)](https://github.com/JordiBForgeFlow) [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | Adds an MRP Scheduler
[mrp_multi_level_estimate](mrp_multi_level_estimate/) | 13.0.1.1.0 | [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | Allows to consider demand estimates using MRP multi level.
[mrp_planned_order_matrix](mrp_planned_order_matrix/) | 13.0.1.0.0 |  | Allows to create fixed planned orders on a grid view.
[mrp_production_grouped_by_product](mrp_production_grouped_by_product/) | 13.0.1.0.2 |  | Production Grouped By Product
[mrp_production_note](mrp_production_note/) | 13.0.1.0.0 |  | Notes in production orders
[mrp_production_putaway_strategy](mrp_production_putaway_strategy/) | 13.0.1.0.0 |  | Applies putaway strategies to manufacturing orders for finished products.
[mrp_production_request](mrp_production_request/) | 13.0.1.0.2 | [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | Allows you to use Manufacturing Request as a previous step to Manufacturing Orders for better manufacture planification.
[mrp_sale_info](mrp_sale_info/) | 13.0.1.0.0 |  | Adds sale information to Manufacturing models
[mrp_stock_orderpoint_manual_procurement](mrp_stock_orderpoint_manual_procurement/) | 13.0.1.0.0 |  | Updates the value of MO Responsible and keeps trackof changes regarding this field
[mrp_unbuild_tracked_raw_material](mrp_unbuild_tracked_raw_material/) | 13.0.1.0.0 | [![bealdav](https://github.com/bealdav.png?size=30px)](https://github.com/bealdav) | Allow to unbuild tracked purchased products
[mrp_warehouse_calendar](mrp_warehouse_calendar/) | 13.0.1.0.0 | [![JordiBForgeFlow](https://github.com/JordiBForgeFlow.png?size=30px)](https://github.com/JordiBForgeFlow) | Considers the warehouse calendars in manufacturing
[mrp_workorder_sequence](mrp_workorder_sequence/) | 13.0.1.0.0 | [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | adds sequence to production work orders.
[mrp_workorder_update_component](mrp_workorder_update_component/) | 13.0.1.0.0 | [![DavidJForgeFlow](https://github.com/DavidJForgeFlow.png?size=30px)](https://github.com/DavidJForgeFlow) | Allows to modify component lines in work orders.
[product_cost_rollup_to_bom](product_cost_rollup_to_bom/) | 13.0.1.0.0 |  | Update BOM costs by rolling up. Adds scheduled job for unattended rollups.
[product_mrp_info](product_mrp_info/) | 13.0.1.0.0 | [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | Adds smart button in product form view linking to manufacturing order list.
[product_quick_bom](product_quick_bom/) | 13.0.1.0.0 | [![sebastienbeau](https://github.com/sebastienbeau.png?size=30px)](https://github.com/sebastienbeau) [![kevinkhao](https://github.com/kevinkhao.png?size=30px)](https://github.com/kevinkhao) | Create the bom directly from the product
[quality_control_mrp_oca](quality_control_mrp_oca/) | 13.0.1.0.0 |  | MRP extension for quality control (OCA)
[quality_control_oca](quality_control_oca/) | 13.0.2.2.0 |  | Generic infrastructure for quality tests.
[quality_control_stock_oca](quality_control_stock_oca/) | 13.0.1.0.2 |  | Quality control - Stock (OCA)
[repair_refurbish](repair_refurbish/) | 13.0.1.0.0 |  | Create refurbished products during repair
[stock_picking_product_kit_helper](stock_picking_product_kit_helper/) | 13.0.1.0.0 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Set quanity in picking line based on product kit quantity
[stock_whole_kit_constraint](stock_whole_kit_constraint/) | 13.0.1.0.0 |  | Avoid to deliver a kit partially

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Odoo Community Association (OCA)
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
