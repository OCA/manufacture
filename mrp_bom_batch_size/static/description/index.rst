MRP - BoM Batch Size
=====================

This module adds batch size configuration to Bills of Materials (BoM) for automatic manufacturing orders.

Features
--------

* **Batch Size Configuration**: Set a default batch size for automatic manufacturing orders
* **Enable/Disable**: Toggle batch size functionality per BoM
* **Procurement Integration**: Automatically splits procurements into batch-sized manufacturing orders
* **Production Split Wizard**: Enhanced split wizard respects BoM batch size configuration
* **Validation**: Ensures batch sizes are positive when enabled

Configuration
-------------

1. **Enable Batch Size**: Navigate to a BoM and enable the "Enable Batch Size" option
2. **Set Batch Size**: Configure the desired batch size in the BoM's product unit of measure
3. **Automatic Splitting**: Procurements will automatically be split into batch-sized manufacturing orders

Usage
-----

1. **Configure BoM**: Edit a BoM and set the batch size
2. **Create Procurement**: Create a procurement or sales order that triggers manufacturing
3. **Automatic Splitting**: The system will create multiple manufacturing orders of the configured batch size
4. **Manual Splitting**: Use the production split wizard with pre-populated batch size

Example
-------

If a product has a BoM with:
- Batch Size: 10 units
- Enable Batch Size: True

A procurement for 25 units will create:
- Manufacturing Order 1: 10 units
- Manufacturing Order 2: 10 units
- Manufacturing Order 3: 5 units

Use Cases
---------

* **Equipment Constraints**: Manufacturing equipment with fixed capacity limits
* **Quality Control**: Consistent batch sizes for quality testing procedures
* **Inventory Management**: Standardized lot sizes for easier tracking
* **Production Planning**: Optimized production scheduling with standard batch quantities

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/manufacture/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/OCA/manufacture/issues/new?body=module:%20mrp_bom_batch_size%0Aversion:%2017.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A-%20...%0A%0A**Expected%20behavior**%0A-%20...>`_.

Credits
=======

Authors
~~~~~~~

* Open Source Integrators

Contributors
~~~~~~~~~~~~

* Open Source Integrators

Maintainers
~~~~~~~~~~~

This module is maintained by the Open Source Integrators team.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is part of the `OCA/manufacture <https://github.com/OCA/manufacture>`_ project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
