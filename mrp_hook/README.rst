===============================
Hooks for enabling advanced MRP
===============================

Technical module that provides the proper framework infrastructure (hooks,
fallback, etc) to enable advanced functionality in the manufacturing area,
as https://github.com/odoo/odoo/pull/8885 hasn't been accepted for v8.

* Hooks in *_bom_explode* method for returning dictionary for consume and
  workcenter lines.
* Provide product and template.

By itself it doesn't provide anything, but serves as base for others modules
to develop its features.

Known issues / Roadmap
======================

* This module fully overwrites _bom_explode method, so any other module
  inheriting this method should take that into account.
* On v9, this module can be removed.

Credits
=======

Contributors
------------

* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
