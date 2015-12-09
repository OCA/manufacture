.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===============================
Hooks for enabling advanced MRP
===============================

Technical module that provides the proper framework infrastructure (hooks,
fallback, etc) to enable advanced functionality in the manufacturing area,
as https://github.com/odoo/odoo/pull/8885 hasn't been accepted for v8:

* Hooks in *_bom_explode* method to return a dictionary for consumption and
  workcenter lines.
* Provide product and template on *_bom_find*.

Usage
=====

By itself it doesn't provide anything visible, but serves as base for others
modules to develop its features.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/129/8.0

Known issues / Roadmap
======================

* This module fully overwrites _bom_explode method, so any other module
  inheriting this method should take this into account.
* On v9, this module can be removed, as the hooks have been integrated.

Credits
=======

Contributors
------------

* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>

Images
------

* Original Odoo MRP icon
* Thanks to https://openclipart.org/detail/151441/lifting-hook

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
