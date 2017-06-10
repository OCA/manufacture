.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================
Mrp Production Properties
=========================

This module adds the properties to the manufacturing order copying them
from the related procurement order.

Installation
============

To install this module, you need to:

1. make sure all dependency modules installed

Configuration
=============

To configure this module, you need to:

1. Add access user mrp who will manage property
2. Activate developer mode
3. Go to Setting > Users select user
4. Check "Manage Properties of Product"
5. Add access user sale to select property on sales
6. Follow poin 3
7. Check "Properties on lines"

.. figure:: path/to/local/image.png
   :alt: alternative description
   :width: 600 px

Usage
=====

To use this module, you need to:

1. User sales make customer order and select product property on line.
2. User sales confirm sales order.
3. User manufacture check MO which have reference and same property with SO.
4. Finish production.
5. Do delivery order sales.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/{repo_id}/{branch}

.. repo_id is available in https://github.com/OCA/maintainer-tools/blob/master/tools/repos_with_ids.txt
.. branch is "8.0" for example


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

* Alex Comba <alex.comba@agilebg.com>
* Sandy Carter <sandy.carter@savoirfairelinux.com>
* Stéphane Bidoul <stephane.bidoul@acsone.eu>
* Pedro M. Baeza <pedro.baeza@gmail.com>
* Bima Wijaya <bimajatiwijaya@gmail.com>


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