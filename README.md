
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/manufacture&target_branch=17.0)
[![Pre-commit Status](https://github.com/OCA/manufacture/actions/workflows/pre-commit.yml/badge.svg?branch=17.0)](https://github.com/OCA/manufacture/actions/workflows/pre-commit.yml?query=branch%3A17.0)
[![Build Status](https://github.com/OCA/manufacture/actions/workflows/test.yml/badge.svg?branch=17.0)](https://github.com/OCA/manufacture/actions/workflows/test.yml?query=branch%3A17.0)
[![codecov](https://codecov.io/gh/OCA/manufacture/branch/17.0/graph/badge.svg)](https://codecov.io/gh/OCA/manufacture)
[![Translation Status](https://translation.odoo-community.org/widgets/manufacture-17-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/manufacture-17-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# manufacture

TODO: add repo description.

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[account_move_line_mrp_info](account_move_line_mrp_info/) | 17.0.1.1.0 |  | Account Move Line Mrp Info
[mrp_attachment_mgmt](mrp_attachment_mgmt/) | 17.0.1.0.0 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Mrp Attachment Mgmt
[mrp_bom_component_menu](mrp_bom_component_menu/) | 17.0.1.0.0 |  | MRP BOM Component Menu
[mrp_bom_hierarchy](mrp_bom_hierarchy/) | 17.0.1.0.0 |  | Make it easy to navigate through BoM hierarchy.
[mrp_bom_tracking](mrp_bom_tracking/) | 17.0.1.0.0 |  | Logs any change to a BoM in the chatter
[mrp_component_operation](mrp_component_operation/) | 17.0.1.0.0 |  | Allows to operate the components from a MO
[mrp_component_operation_scrap_reason](mrp_component_operation_scrap_reason/) | 17.0.1.0.0 |  | Allows to pass a reason to scrap with MRP component operation
[mrp_mass_production_order](mrp_mass_production_order/) | 17.0.2.1.1 | [![peluko00](https://github.com/peluko00.png?size=30px)](https://github.com/peluko00) | Create multiple manufacturing orders in one step
[mrp_multi_level](mrp_multi_level/) | 17.0.1.2.8 | [![JordiBForgeFlow](https://github.com/JordiBForgeFlow.png?size=30px)](https://github.com/JordiBForgeFlow) [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | Adds an MRP Scheduler
[mrp_multi_level_estimate](mrp_multi_level_estimate/) | 17.0.1.0.0 | [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | Allows to consider demand estimates using MRP multi level.
[mrp_planned_order_matrix](mrp_planned_order_matrix/) | 17.0.1.0.0 |  | Allows to create fixed planned orders on a grid view.
[mrp_production_back_to_draft](mrp_production_back_to_draft/) | 17.0.1.0.1 |  | Allows to return to draft a confirmed or cancelled MO.
[mrp_production_note](mrp_production_note/) | 17.0.1.0.0 |  | Notes in production orders
[mrp_production_picking_type_from_route](mrp_production_picking_type_from_route/) | 17.0.1.0.0 |  | Updates the operation type creating MO based on the product
[mrp_production_quant_manual_assign](mrp_production_quant_manual_assign/) | 17.0.1.0.1 |  | Production - Manual Quant Assignment
[mrp_production_serial_matrix](mrp_production_serial_matrix/) | 17.0.1.1.0 |  | MRP Production Serial Matrix
[mrp_repair_order](mrp_repair_order/) | 17.0.1.0.0 | [![peluko00](https://github.com/peluko00.png?size=30px)](https://github.com/peluko00) | Create repair order from manufacturing order
[mrp_sale_info](mrp_sale_info/) | 17.0.1.1.0 |  | Adds sale information to Manufacturing models
[mrp_subcontracting_bom_dual_use](mrp_subcontracting_bom_dual_use/) | 17.0.1.0.1 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Mrp subcontracting bom dual use
[mrp_subcontracting_purchase_link](mrp_subcontracting_purchase_link/) | 17.0.1.0.0 |  | Link Purchase Order Line to Subcontract Productions
[mrp_tag](mrp_tag/) | 17.0.1.0.0 |  | Allows to add multiple tags to Manufacturing Orders
[mrp_warehouse_calendar](mrp_warehouse_calendar/) | 17.0.1.0.0 | [![JordiBForgeFlow](https://github.com/JordiBForgeFlow.png?size=30px)](https://github.com/JordiBForgeFlow) | Considers the warehouse calendars in manufacturing
[mrp_workorder_sequence](mrp_workorder_sequence/) | 17.0.1.0.0 | [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | adds sequence to production work orders.
[purchase_mrp_distribution](purchase_mrp_distribution/) | 17.0.1.0.0 |  | Purchase MRP Distribution
[quality_control_mrp_oca](quality_control_mrp_oca/) | 17.0.1.0.0 |  | MRP extension for quality control (OCA)
[quality_control_oca](quality_control_oca/) | 17.0.1.1.0 |  | Generic infrastructure for quality tests.
[quality_control_oca_timesheet](quality_control_oca_timesheet/) | 17.0.1.0.0 | [![ppyczko](https://github.com/ppyczko.png?size=30px)](https://github.com/ppyczko) | Quality Control - Timesheet (OCA)
[quality_control_stock_oca](quality_control_stock_oca/) | 17.0.2.0.0 |  | Quality control - Stock (OCA)

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
