  .. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===============================
Don't confirm MOs when procured
===============================

This module prevents the automatic confirmation of manufacturing order when
procurement orders are executed.

Installation
============

To install this module, you need to:

1.  Clone the branch 8.0 of the repository https://github.com/OCA/manufacture
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list
4.  Go to menu *Setting -> Modules -> Local Modules*
5.  Search For *Procurement MRP no Confirm*
6.  Install the module

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/129/8.0


Known issues / Roadmap
======================

* If the production order workflow has been altered in the transition
  *prod_trans_draft_picking* to have another condition, when uninstalling this
  module, you will need to restore the custom condition.

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

* Pedro M. Baeza <pedro.baeza@tecnativa.com>
* Ainara Galdona <agaldona@avanzosc.es>
* Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>
* Andhitia Rama <andhitia.r@opensynergy-indonesia.com>

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
