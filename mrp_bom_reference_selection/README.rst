.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

========================================
MRP Bill of Material Reference Selection
========================================

This module allows to select the component in a BoM when you have several BoM for one product.
This is used to manage versions of a product.
Produced lot contains a reference to the bill of material used to compute the lot.

Installation
============

To install this module, you just need to select the module and ensure yourself dependencies are available.

Configuration
=============

No particular configuration to use this module.

Usage
=====

To use this module, you need to :

- create a product
- create a BoM from this product (ie : AA), give a reference to this BoM (ie : A1)
- create an other BoM for the same product, give a reference to this BoM (ie : A2)
- now, you can create an other BoM for an other product (ie : BB) with products AA as component. You will have to choose the BoM you want between A1 or A2

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/129/8.0


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/manufacture/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback <https://github.com/OCA/manufacture/issues/new?body=module:%20mrp_bom_reference%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Module developed and tested with Odoo version 8.0
For questions, please contact our support services <support@savoirfairelinux.com>

Contributors
------------

* David DUFRESNE <david.dufresne@savoirfairelinux.com>
* Jordi RIERA <jordi.riera@savoirfairelinux.com>
* Bruno JOLIVEAU <bruno.joliveau@savoirfairelinux.com>

Icon
----
* http://en.wikipedia.org/wiki/File:People%27s_Action_Party_of_Singapore_logo.svg

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
