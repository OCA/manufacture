.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================
MRP MTO with Stock
==================

This module extends the functionality of Manufacturing to support the creation
of procurements only for a part of the raw material.
It has 2 modes. The default one allow you to pull
from stock until the quantity on hand is zero, and then create a procurement
to fulfill the MO requirements. In this mode, the created procurements must
be the ones fulfilling the MO that has generated it.
The other mode is based on the forecast quantity. It will allow to pull from
stock until the forecast quantity is zero and then create a procurement for
the missing products. In this mode, there is no link between the procurement
created and MO that has generated it. The procurement may be used to fulfill
another MO.

Configuration
=============

To configure this module, you need to:

#. Go to the products you want to follow this behaviour.
#. In the view form go to the tab *Inventory* and set the *Manufacturing
   MTO/MTS Locations*. Any other location not specified here will have the
   standard behavior.

If you want to use the second mode, based on forecast quantity

#. Go to the warehouse you want to follow this behaviour.
#. In the view form go to the tab *Warehouse Configuration* and set the 
   *MRP MTO with forecast stock*. You still need to configure the products
   like described in last step.

Usage
=====

To use this module, you need to:

#. Go to *Manufacturing* and create a Manufacturing Order.
#. Click on *Check availability*.

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

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* John Walsh <John.Walsh@interclean.com>
* Lois Rilo <lois.rilo@eficent.com>
* Florian da Costa <florian.dacosta@akretion.com>
* Bhavesh Odedra <bodedra@opensourceintegrators.com>

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
