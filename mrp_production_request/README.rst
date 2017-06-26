.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================
MRP Production Request
======================

This module extends the functionality of Manufacturing to allow you to use
Manufacturing Request (MR) as a previous step to Manufacturing Orders (MO).

Configuration
=============

To configure this module to automatically generate Manufacturing Requests
from procurement orders instead of directly create manufacturing orders yo
need to:

#. Go to the products that you want them to trigger manufacturing orders.
#. Go to the *Inventory* tab.
#. Check the route *manufacture* and the box *Manufacturing Request*.

Usage
=====

To use this module, you need to:

#. Go to *Manufacturing > Manufacturing Requests*.
#. Create a manufacturing request or open a existing one (assigned to you or
   created from a procurement).
#. If you click on *Request approval* button the user assigned as approver
   will added to the thread.
#. If you are the approver you can either click on *Approve* or *Reject*
   buttons.
#. Rejecting a MR will cancel associated procurements and propagate this
   cancellation.
#. Approving a MR will allow to create manufacturing orders.
#. You can manually set to done a request by clicking in the button *Done*.

To create MOs from MRs you have to:

#. Go to approved manufacturing request.
#. Click on the button *Create Manufacturing Order*.
#. In the opened wizard, click on *Compute lines* so you will have a
   quantity proposed for creating a MO. This quantity is the maximum quantity
   you can produce with the current stock available in the source location.
#. Use the proposed quantity or change it and click on *Create MO* at the
   bottom of the wizard.

**NOTE:** This module does not restrict the quantity that can be converted
from a MR to MOs. It is in hands of the user to decide when a MR is ended and
to set it to *Done* state.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/129/9.0

Known issues / Roadmap
======================

* Take into account workstations.
* Take into account consumable products.

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

* Lois Rilo Antelo <lois.rilo@eficent.com>
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
