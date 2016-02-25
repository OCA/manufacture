.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================================
Real costs in manufacturing orders
==================================

This module allows to manage the control of Manufacturing Orders actual costs,
by creating analytic lines as defined in the MO (from *mrp_project*).

It also updates product standard price when a manufacturing orders is finished
according this formula:

(Product stock * Product standard price + Production real cost) /
(Product stock + Final product quantity)

Installation
============

This module depends on the module *product_variant_cost_price*, that is
available in:

https://github.com/OCA/product-variant

Usage
=====

Processing a manufacture order, analytic entries adding costs will be
created when:

* Some raw material is consumed.
* A work order is finished or paused.
* Also, together with *project_timesheet* module, users time is also translated
  to costs in the linked analytic account.

The sum of all these analytic entries is the real cost:

.. figure:: mrp_production_real_cost/static/description/mrp_real_cost.png
   :alt: MRP Real Cost Details

Cost/cycle = all overhead costs associated with running one work centre cycle
(where a cycle is the Number of Cycles as calculated in the Work Order).

Cost/hr = calculated as all overhead costs associated with running the work
centre (excluding any costs covered in the cost per cycle) / the number of
hours the work centre is operating.

Pre-operation cost = Time before prod. x cost of the Pre-operation costing
product

Post-operation cost = Time after prod. x cost of the Post-operation costing
product

It’s up to the user to determine overhead costs as accurately as possible
and use all, some or none of them in order to reflect their manufacturing
process.


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/129/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/manufacture/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
manufacture/issues/new?body=module:%20
mrp_production_real_cost%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
* Ana Juaristi <ajuaristio@gmail.com>
* Ainara Galdona <agaldona@avanzosc.es>
* Antonio Espinosa <antonioea@antiun.com>

Images
------

* Original Odoo MRP icon
* Thanks to https://openclipart.org/detail/224801/black-and-white-calculator

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.