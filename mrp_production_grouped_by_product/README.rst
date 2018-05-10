.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=============================
Production Grouped By Product
=============================

When you have several sales orders with make to (MTO) order products that
require to be manufactured, you end up with one manufacturing order for each of
these sales orders, which is very bad for the management.

With this module, each time an MTO manufacturing order is required to be
created, it first checks that there's no other existing order not yet started
for the same product and bill of materials, and if there's one, then the
quantity of that order is increased instead of creating a new one.

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/129/11.0

Known issues / Roadmap
======================

* Add a check in the product form for excluding it from being grouped.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/manufacture/issues>`_. In case of trouble,
please check there if your issue has already been reported. If you spotted it
first, help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Tecnativa <https://www.tecnativa.com>_

  * David Vidal
  * Pedro M. Baeza

Do not contact contributors directly about support or help with technical issues.

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
