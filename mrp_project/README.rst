.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================
MRP Project Link
================

This module links projects and tasks to *manufacturing orders* (MO) and
*work orders* (WO).

Installation
============

It depends on the module *mrp_analytic*, that is hosted on
OCA/account-analytic: https://github.com/OCA/account-analytic

Usage
=====

In a manufacturing order (MO), you can select a project to be attached to it.
If none is selected, a project is automatically created when the MO is
confirmed.

When the MO starts, a task is created and assigned to the order.

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
mrp_project%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Images
------

* Original Odoo icons.
* Thanks to https://openclipart.org/detail/15193/Arrow%20set%20%28Comic%29

Contributors
------------

* Daniel Campos <danielcampos@avanzosc.es>
* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
* Antonio Espinosa <antonioea@antiun.com>

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
