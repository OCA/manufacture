.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===============================================
Create Procurement Group On Manufacturing Order
===============================================

This module adds ability to group manufacturing order's raw material moves, and
other moves created by it's pull flow, by given procurement group.

Installation
============

To install this module, you need to:

1.  Clone the branch 8.0 of the repository https://github.com/OCA/manufacture
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list
4.  Go to menu *Setting -> Modules -> Local Modules*
5.  Search For *Create Procurement Group On Manufacturing Order*
6.  Install the module


Usage
=====

To use this module, you need to:

1. Go to menu *Manufacturing -> Manufacturing -> Manufacturing Orders*
2. Create manufacturing order. Do not forget to fill *Raw Material Procurement Group*
3. When MO is confirmed. Raw material moves with *make to order* procurement method, and it's
   other moves created by it's pull flow, will be grouped based on *Raw Material Procurement Group*
   given


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/129/8.0


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/manufacture/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Andhitia Rama <andhitia.r@gmail.com>
* Lois Rilo <lois.rilo@eficent.com>

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
