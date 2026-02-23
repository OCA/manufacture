.. image:: https://odoo-community.org/readme-banner-image
   :target: https://odoo-community.org/get-involved?utm_source=readme
   :alt: Odoo Community Association

=====================
BOM Attribute Match
=====================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/license-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OCA%2Fmanufacture-lightgray.png?logo=github
    :target: https://github.com/OCA/manufacture/tree/19.0/mrp_bom_attribute_match
    :alt: OCA/manufacture
.. |badge4| image:: https://img.shields.io/badge/weblate-Translate%20me-F47D42.png
    :target: https://translation.odoo-community.org/projects/manufacture-19-0/manufacture-19-0-mrp_bom_attribute_match
    :alt: Translate me on Weblate
.. |badge5| image:: https://img.shields.io/badge/runboat-Try%20me-875A7B.png
    :target: https://runboat.odoo-community.org/builds?repo=OCA/manufacture&target_branch=19.0
    :alt: Try me on Runboat

|badge1| |badge2| |badge3| |badge4| |badge5|

This module allows you to use dynamic BOM components based on product attributes.
Instead of specifying a specific product variant in the BOM, you can specify a
product template, and the system will automatically select the correct variant
based on the attributes of the manufactured product.

**Table of contents**

.. contents::
   :local:

Configuration
=============

To use this module:

1. Go to Manufacturing > Products > Bills of Materials
2. Create or edit a BOM
3. In a BOM line, instead of selecting a specific product (variant), select a Product Template
4. The system will automatically match the component variant based on the manufactured product's attributes

Usage
=====

When you create a manufacturing order, the system will:

1. Check the attributes of the product being manufactured
2. Find the matching component variant from the Product Template
3. Use that variant in the manufacturing order

For example:
- Manufacturing product: T-Shirt (Red, L)
- Component template: Fabric
- System automatically selects: Fabric (Red, L)

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/manufacture/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/OCA/manufacture/issues/new?body=module:%20mrp_bom_attribute_match%0Aversion:%2019.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
-------

* Ilyas
* Ooops
* CHEF PIXEL

Contributors
------------

- Ooops404 <https://ooops404.com>

  - Ilyas

- `Camptocamp <https://www.camptocamp.com>`__:

  - Iván Todorovich <ivan.todorovich@camptocamp.com>

- `Studio73 <https://www.studio73.es>`__:

  - Eugenio Micó <eugenio@studio73.es>

- `CHEF PIXEL <https://chef-pixel.fr>`__:

  - Support: hello@chef-pixel.fr

Other credits
-------------

The development of this module has been financially supported by:

- Ooops404
- Camptocamp
- Studio73
- CHEF PIXEL

Maintainers
-----------

This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

This module is part of the `OCA/manufacture <https://github.com/OCA/manufacture/tree/19.0/mrp_bom_attribute_match>`_ project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
