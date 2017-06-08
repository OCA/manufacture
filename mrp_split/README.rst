.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========
Mrp Split
=========

This module extends the functionality of Manufacturing to allow you to split
existing Manufacturing Order (MO) in *New* or *Awaiting Raw Materials* state.
The proposed quantity to split will ensure that the originating MO will be
ready to produce (if possible).

Usage
=====

To use this module, you need to:

#. Go to *Manufacturing > Manufacturing Orders*.
#. Open a Manufacturing Order in state *New* or *Awaiting Raw Materials*.
#. Click the button *Split MO*.
#. In the wizard, click on *Compute lines* to get a quantity recommendation to
   split.
#. Change the *Quantity to split* if desired and click on *Split* button at
   the bottom of the form.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/129/9.0

Known issues / Roadmap
======================

* Take into account consumable products.
* Picking direct validation lead to error.
* Add security group related to splitting MOs?
* Cancelled stock moves are shown as consumed raw materials.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/{project_repo}/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Lois Rilo <lois.rilo@eficent.com>
* Jordi Ballester <jordi.ballester@eficent.com>

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
