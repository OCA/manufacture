.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

Procurement Improvement - supply method
=======================================

This module aims to add more flexibility on procurement management.
  * Allowing planner changing the supply method on the procurement order level
        by adding a new field supply_method for planner to modify.

  * Allowing planner changing the procurement method and supply method
        before the procurement order is running.

Business case:
    One company might purchase from one company or produce in another company
        for the same product, the planner can change the supply method
        on the procurement order level instead of having two products
        with different supply methods.

Please note that this module re-defines the field: procure_method
    which is defined in module: procurement.

Installation
============

To install this module, you need to:

 * have basic modules installed (sale, mrp, procurement, purchase)

Configuration
=============

To configure this module, you need to:

 * No specific configuration needed.

Usage
=====


For further information, please visit:

 * https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================


Credits
=======


Contributors
------------

* Alex Duan <alex.duan@elico-corp.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization
    whose mission is to support the collaborative development of Odoo features
        and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org. 