.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3

=================================
Barcode Scanning in Manufacturing
=================================

This module allows you to use a barcode scanner to avoid clicking in the tablet interface of the MRP module.

Installation
============

This module depends on the enterprise module "quality_mrp".

Configuration
=============

Print the following `document <https://github.com/OCA/manufacture/blob/master/mrp_barcode/static/description/Barcode.pdf>`_ to have the barcode of the manufacturing operations:

* Validate
* Mark as done
* Pass (quality check)
* Fail (quality check)

Barcodes were generated thanks to `https://barcode.tec-it.com/en/Code128 <https://barcode.tec-it.com/en/Code128>`_.

Usage
=====

* Go to Manufacturing
* Click on the "Work Orders" button of your work center
* Open the first one and start scanning

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

* Maxime Chambreuil <mchambreuil@opensourceintegrators.com>

Funders
-------

The development of this module has been financially supported by:

* Open Source Integrators <https://www.opensourceintegrators.com>

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
