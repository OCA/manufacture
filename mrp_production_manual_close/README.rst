.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

MRP Production manual close
===========================

This module modifies mrp production workflow to finish the production orders
manually adding a new close button.

Known issues / Roadmap
======================

When there are pending movements to finish production order, it will cancel all
movements (including pending procurement orders) and will mark the production
as done.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/manufacture/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback <https://github.com/OCA/manufacture/issues/new?body=module:%20mrp_production_manual_close%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------
* Daniel Campos <danielcampos@avanzosc.es>
* Pedro M. Baeza <pedro.baeza@tecnativa.com>
* Ana Juaristi <ajuaristio@gmail.com>


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