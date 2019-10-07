This module allows you to calculate, based in known inventory, demand, and
supply, and based on parameters set at product variant level, the new
procurements for each product.

To do this, the calculation starts at top level of the bill of material
and explodes this down to the lowest level.

Key Features
------------

* MRP parameters set by product variant MRP area pairs.
* Cron job to calculate the MRP demand.
* Manually calculate the MRP demand.
* Confirm the calculated MRP demand and create PO's, or MO's.
* Able to see the products for which action is needed throught Planned Orders.
* Integration with `Stock Demand Estimates <https://github.com/OCA/stock-logistics-warehouse/tree/12.0/stock_demand_estimate>`_ system.
  Note: You need to install `mrp_multi_level_estimate module <https://github.com/OCA/manufacture/tree/12.0/mrp_multi_level_estimate>`_.
