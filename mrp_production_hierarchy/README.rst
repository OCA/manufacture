.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

===========================
Production Orders Hierarchy
===========================

This module allows to view the hierarchy of generated production orders
when several levels of bill of materials are involved.

Usage
=====

Create a new production order (Manufacture / Operations / Manufacturing Orders)
with a multi-levels nomenclatured product, and related products configured with
'Manufacture' and 'Make To Order' routes:

.. figure:: mrp_production_hierarchy/static/description/mrp_production_hierarchy_1.png

Once saved, click on the 'Hierarchy' button at right:

.. figure:: mrp_production_hierarchy/static/description/mrp_production_hierarchy_2.png

.. figure:: mrp_production_hierarchy/static/description/mrp_production_hierarchy_3.png

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/129/10.0

Known issues / Roadmap
======================

* Only new production orders will benefit from this feature, it is not compatible with existing orders.

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

* Odoo Community Association: `Icon <https://odoo-community.org/logo.png>`_.

Contributors
------------

* Sébastien Alix <sebastien.alix@osiell.com> (https://osiell.com)

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
