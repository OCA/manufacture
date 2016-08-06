.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=====================================
MRP Operations start without material
=====================================

This module allows to start WO without having the material assigned.

Installation
============

To install this module, you need to:

1.  Clone the branch 8.0 of the repository https://github.com/OCA/manufacture
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list
4.  Go to menu *Setting -> Modules -> Local Modules*
5.  Search For *MRP Operations start without material*
6.  Install the module

Usage
=====

To configure operation can be started without material, you need to:

1. Go to menu *Manufacture -> Configuration -> Routings*
2. Open/create routing data
3. Open/create one of the routing operation
4. Activate *Init without material* option

After configuration, everytime that operation create, user can start work order without
material assign.

To start work order without material assigned, you need to:

1. Go to menu *Manufacture -> Manufacture -> Workorder*
2. Open/create work order
3. Activate *Init without material* option

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

* Daniel Campos <danielcampos@avanzosc.es>
* Pedro M. Baeza <pedro.baeza@tecnativa.com>
* Ana Juaristi <ajuaristio@gmail.com>
* OpenSynergy Indonesia <https://opensynergy-indonesia.com>

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
