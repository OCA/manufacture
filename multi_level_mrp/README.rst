.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===============
Multi Level MRP
===============

This module allows you to calculate, based in known inventory, demand, and
supply, and based on parameters set at product variant level, the new
procurements for each product.

To do this, the calculation starts at top level of the bill of material
and explodes this down to the lowest level.

Key Features
------------
* MRP parameters at product variant level
* Basic forecast system
* Cron job to calculate the MRP demand
* Manually calculate the MRP demand
* Confirm the calculated MRP demand and create BID's, PO's, or MO's
* View to see the products for which action is needed


Installation
============


Usage
=====


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/129/11.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/manufacture/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Original Odoo icons.


Contributors
------------

* Wim Audenaert <wim.audenaert@ucamco.com>
* Jordi Ballester <jordi.ballester@eficent.com>
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
