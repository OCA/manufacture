MRP Bill of Material Reference Selection
========================================

This module allows to select the component in a bom when you have several bom for one product.
This is used to manage versions of a product.
Produced lot contains a reference to the bill of material used to compute the lot.

Installation
============

To install this module, you just need to select the module and insure yourself dependancies are available.

Configuration
=============

No particular configuration to use this module.


Usage
=====

To use this module, you need to :
- create a product
- create a bom from this product (ie : AA), give a reference to this bom (ie : A1)
- create an other bom for the same product, give a reference to this bom (ie : A2)
- now, you can create an other bom for an other product (ie : BB) with products AA as component. You will have to choose the bom you want between A1 or A2


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

Odoo Community Association

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
