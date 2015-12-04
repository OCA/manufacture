.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================================
MRP Project Link (with operations)
==================================

This module links manufacturing operations with projects. It performs the
following actions:

* Auto-create tasks for work orders with assigned operators.
* Add a tab where to encode task for the work order.
* Add a link on task for the work order scheduled product.

Installation
============

This modules is auto-installed when you install *mrp_operations_extension* and
*mrp_project*.

Usage
=====

In a manufacturing order (MO) containing work orders with at least one operator
assigned, when a work order is started, a task is created and assigned to the
operator.

In the work order form, a new tab "Operators time" is added to input the the
work log.

Besides, in the related tasks, the products scheduled in the work order are
listed.

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
mrp_operations_project%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Daniel Campos <danielcampos@avanzosc.es>
* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>

Images
------

* Original Odoo icons.
* Thanks to https://openclipart.org/detail/15193/Arrow%20set%20%28Comic%29
* Thanks to https://openclipart.org/detail/151831/work-bench

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
