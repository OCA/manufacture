
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/manufacture&target_branch=12.0)
[![Pre-commit Status](https://github.com/OCA/manufacture/actions/workflows/pre-commit.yml/badge.svg?branch=12.0)](https://github.com/OCA/manufacture/actions/workflows/pre-commit.yml?query=branch%3A12.0)
[![Build Status](https://github.com/OCA/manufacture/actions/workflows/test.yml/badge.svg?branch=12.0)](https://github.com/OCA/manufacture/actions/workflows/test.yml?query=branch%3A12.0)
[![codecov](https://codecov.io/gh/OCA/manufacture/branch/12.0/graph/badge.svg)](https://codecov.io/gh/OCA/manufacture)
[![Translation Status](https://translation.odoo-community.org/widgets/manufacture-12-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/manufacture-12-0/?utm_source=widget)

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
[account_move_line_manufacture_info](account_move_line_manufacture_info/) | 12.0.1.0.1 |  | Account Move Line Manufacture Information
[base_repair](base_repair/) | 12.0.1.1.1 | [![marcelsavegnago](https://github.com/marcelsavegnago.png?size=30px)](https://github.com/marcelsavegnago) | This module extends the functionality of Odoo Repair module to add some basic features.
[base_repair_config](base_repair_config/) | 12.0.1.0.2 | [![marcelsavegnago](https://github.com/marcelsavegnago.png?size=30px)](https://github.com/marcelsavegnago) | Provides general settings for the Repair App
[mrp_auto_assign](mrp_auto_assign/) | 12.0.1.0.0 |  | Make MO automatically reserve raw material moves at creation
[mrp_auto_create_lot](mrp_auto_create_lot/) | 12.0.1.0.1 | [![ps-tubtim](https://github.com/ps-tubtim.png?size=30px)](https://github.com/ps-tubtim) | Auto create lots for work orders
[mrp_bom_comparison](mrp_bom_comparison/) | 12.0.1.0.1 |  | Compare two Bill of Materials to view the differences
[mrp_bom_component_menu](mrp_bom_component_menu/) | 12.0.1.0.0 |  | MRP BOM Component Menu
[mrp_bom_line_sequence](mrp_bom_line_sequence/) | 12.0.1.0.1 |  | Manages the order of BOM lines by displaying its sequence
[mrp_bom_location](mrp_bom_location/) | 12.0.1.0.2 |  | Adds location field to Bill of Materials and its components.
[mrp_bom_multi_company](mrp_bom_multi_company/) | 12.0.1.0.1 |  | Multi Company Bill of Materials
[mrp_bom_note](mrp_bom_note/) | 12.0.1.0.0 |  | Notes in Bill of Materials
[mrp_bom_tracking](mrp_bom_tracking/) | 12.0.1.0.1 |  | Logs any change to a BoM in the chatter
[mrp_bom_widget_section_and_note_one2many](mrp_bom_widget_section_and_note_one2many/) | 12.0.1.1.0 |  | Add section and note in Bills of Materials
[mrp_mto_with_stock](mrp_mto_with_stock/) | 12.0.1.0.1 |  | Fix Manufacturing orders to pull from stock until qty is zero, and then create a procurement for them.
[mrp_multi_level](mrp_multi_level/) | 12.0.2.4.1 | [![JordiBForgeFlow](https://github.com/JordiBForgeFlow.png?size=30px)](https://github.com/JordiBForgeFlow) [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | Adds an MRP Scheduler
[mrp_multi_level_estimate](mrp_multi_level_estimate/) | 12.0.1.1.0 | [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | Allows to consider demand estimates using MRP multi level.
[mrp_planned_order_matrix](mrp_planned_order_matrix/) | 12.0.1.0.2 |  | Allows to create fixed planned orders on a grid view.
[mrp_production_auto_post_inventory](mrp_production_auto_post_inventory/) | 12.0.1.1.1 |  | Production Auto Post-Inventory
[mrp_production_filter_lot](mrp_production_filter_lot/) | 12.0.1.0.1 |  | In production order production popup, filter lots based on their location and availability
[mrp_production_grouped_by_product](mrp_production_grouped_by_product/) | 12.0.1.0.1 |  | Production Grouped By Product
[mrp_production_hierarchy](mrp_production_hierarchy/) | 12.0.1.0.1 |  | View the hierarchy of generated production orders
[mrp_production_note](mrp_production_note/) | 12.0.1.0.0 |  | Notes in production orders
[mrp_production_putaway_strategy](mrp_production_putaway_strategy/) | 12.0.1.0.1 |  | Applies putaway strategies to manufacturing orders for finished products.
[mrp_production_quant_manual_assign](mrp_production_quant_manual_assign/) | 12.0.1.0.0 |  | Production - Manual Quant Assignment
[mrp_production_request](mrp_production_request/) | 12.0.1.0.1 | [![lreficent](https://github.com/lreficent.png?size=30px)](https://github.com/lreficent) | Allows you to use Manufacturing Request as a previous step to Manufacturing Orders for better manufacture planification.
[mrp_production_show_post_inventory](mrp_production_show_post_inventory/) | 12.0.1.0.2 |  | Production Show Post Inventory
[mrp_progress_button](mrp_progress_button/) | 12.0.1.0.0 |  | Add a button on MO to make the MO state 'In Progress'
[mrp_request_bom_structure](mrp_request_bom_structure/) | 12.0.1.0.0 |  | Shortcut between Manufacturing Request and Bom report
[mrp_request_workcenter_cycle](mrp_request_workcenter_cycle/) | 12.0.1.0.1 | [![bealdav](https://github.com/bealdav.png?size=30px)](https://github.com/bealdav) | MRP Request Workcenter Cycle
[mrp_sale_info](mrp_sale_info/) | 12.0.2.0.0 |  | Adds sale information to Manufacturing models
[mrp_stock_orderpoint_manual_procurement](mrp_stock_orderpoint_manual_procurement/) | 12.0.1.0.1 |  | Updates the value of MO Responsible and keeps trackof changes regarding this field
[mrp_subcontracting](mrp_subcontracting/) | 12.0.1.0.6 |  | Subcontract Productions
[mrp_subcontracting_purchase_link](mrp_subcontracting_purchase_link/) | 12.0.1.0.0 |  | Link Purchase Order to Subcontract Productions
[mrp_unbuild_tracked_raw_material](mrp_unbuild_tracked_raw_material/) | 12.0.1.0.0 | [![bealdav](https://github.com/bealdav.png?size=30px)](https://github.com/bealdav) | Allow to unbuild tracked purchased products
[mrp_warehouse_calendar](mrp_warehouse_calendar/) | 12.0.1.0.2 | [![jbeficent](https://github.com/jbeficent.png?size=30px)](https://github.com/jbeficent) | Considers the warehouse calendars in manufacturing
[mrp_workorder_sequence](mrp_workorder_sequence/) | 12.0.1.0.1 | [![lreficent](https://github.com/lreficent.png?size=30px)](https://github.com/lreficent) | adds sequence to production work orders.
[product_mrp_info](product_mrp_info/) | 12.0.1.0.1 | [![lreficent](https://github.com/lreficent.png?size=30px)](https://github.com/lreficent) | Adds smart button in product form view linking to manufacturing order list.
[product_quick_bom](product_quick_bom/) | 12.0.1.0.0 | [![sebastienbeau](https://github.com/sebastienbeau.png?size=30px)](https://github.com/sebastienbeau) [![kevinkhao](https://github.com/kevinkhao.png?size=30px)](https://github.com/kevinkhao) | Create the bom directly from the product
[quality_control](quality_control/) | 12.0.1.5.1 |  | Generic infrastructure for quality tests.
[quality_control_issue](quality_control_issue/) | 12.0.1.0.1 | [![lreficent](https://github.com/lreficent.png?size=30px)](https://github.com/lreficent) | Allow to manage and report Quality Control Issues.
[quality_control_mrp](quality_control_mrp/) | 12.0.1.0.1 |  | MRP extension for quality control
[quality_control_stock](quality_control_stock/) | 12.0.1.0.3 |  | Quality control - Stock
[quality_control_team](quality_control_team/) | 12.0.1.1.1 | [![lreficent](https://github.com/lreficent.png?size=30px)](https://github.com/lreficent) | Adds quality control teams to handle different quality control workflows
[repair_calendar_view](repair_calendar_view/) | 12.0.1.1.1 |  | Repair Calendar View
[repair_default_terms_conditions](repair_default_terms_conditions/) | 12.0.1.0.0 | [![marcelsavegnago](https://github.com/marcelsavegnago.png?size=30px)](https://github.com/marcelsavegnago) | This module allows repair default terms & conditions
[repair_discount](repair_discount/) | 12.0.1.0.1 |  | Repair Discount
[repair_payment_term](repair_payment_term/) | 12.0.1.0.1 | [![mileo](https://github.com/mileo.png?size=30px)](https://github.com/mileo) | This module add to Repair Orders the *Payment Term* field
[repair_quality_control_issue](repair_quality_control_issue/) | 12.0.1.0.1 | [![cubells](https://github.com/cubells.png?size=30px)](https://github.com/cubells) | Add the possibility to create repairs orders from quality control issues.
[repair_refurbish](repair_refurbish/) | 12.0.1.1.3 |  | Create refurbished products during repair
[repair_timeline](repair_timeline/) | 12.0.1.0.2 | [![marcelsavegnago](https://github.com/marcelsavegnago.png?size=30px)](https://github.com/marcelsavegnago) | Add timeline view
[stock_mts_mto_rule_mrp](stock_mts_mto_rule_mrp/) | 12.0.1.0.0 |  | Add support for MTS+MTO route on manufacturing
[stock_picking_product_kit_helper](stock_picking_product_kit_helper/) | 12.0.1.0.0 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Set quanity in picking line based on product kit quantity
[stock_whole_kit_constraint](stock_whole_kit_constraint/) | 12.0.1.0.0 |  | Avoid to deliver a kit partially

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
