.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================================
Estimated costs in manufacturing orders
=======================================

This module extends the functionality of MRP adding estimates for Manufacturing
Orders costs, as followed:

* Raw Material cost: for each material to be consumed in the MO, an analytic
  line is generated at product cos
* Operators time: for the time recorded by the operators during each operation,
  one analytic line will be generated (number of lines to be equal to the
  number of operators).
* Machine time: for each operation, one analytic line will be created in the
  associated routing, taking whether the hourly cost or, if missing, the cost
  per cycle.

This module also allows to create some manufacturing orders called "virtual",
that don't permit to be confirmed, but include the buttons for estimating the
costs of the selected manufactured product.

Installation
============

This module depends on the module *product_variant_cost_price*, that is
available in:

https://github.com/OCA/product-variant

Usage
=====

When the manufacturing order is confirmed, analytic lines
are automatically generated in order to estimate the costs of the production

A new menu is available "Virtual Manufacturing Orders for cost estimation"
where the user can managed virtual MO:

* When a new MO is created and the new field "active" is false, the MO will be
  considered virtual. It is only used for cost estimation and can not be
  confirmed.
* To estimate the cost of the MO, the user has to press the button "Compute
  data" in the tab "Work Orders".
* These virtual MO have a separate sequence number.
* The user can create a virtual MO directly from the product form.


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
mrp_production_estimated_cost%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Alfredo de la Fuente <alfredodelafuente@avanzosc.es>
* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
* Ana Juaristi <ajuaristio@gmail.com>
* Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>
* Ainara Galdona <agaldona@avanzosc.es>

Images
------

* Original Odoo MRP icon
* Thanks to https://openclipart.org/detail/120511/budget

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
