.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===============================
MRP Production Putaway Strategy
===============================

This module allows to apply putaway strategies to the products resulting from
the manufacturing orders.

The finished products will be placed in the location designated by the putaway
strategy (if they do not have another destination move), based on the
finished products location that was defined in the manufacturing order.

Configuration
=============

To configure a putaway strategy follow the next steps:

#. Go to 'Inventory / Settings' and activate the option 'Advanced routing of
   products using rules'.
#. Define a putaway strategy in the location zone where the finished products
   are supposed to be placed, and indicate the specific sub-location/bin
   where the products should be placed.

Usage
=====

To use this module proceed as follows:

#. Create a manufacturing order and indicate the product and the finished
   products location zone.
#. Confirm the manufacturing order.
#. You will notice that the finished products location has changed to the
   putaway location, and the chatter shows a message indicating that the
   putaway strategy was applied.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/129/10.0


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
