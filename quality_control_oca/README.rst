.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

===============
Quality control
===============

This module provides a generic infrastructure for quality tests. The idea is
that it can be later reused for doing quality inspections on production lots
or any other area of the company.

Configuration
=============

* Question: The thing to be checked. We have two types of questions:

* Qualitative: The result is a description, color, yes, no...

* Quantitative: The result must be within a range.

* Possible values: The values chosen in qualitative questions.

* Test: The set of questions to be used in inspections.

* Once these values are set, we define the inspection.

We have a *generic* test that can be applied to any model: shipments,
invoices or product, or a *test related*, making it specific to a particular
product and that eg apply whenever food is sold or when creating a batch.

Once these parameters are set, we can just pass the test. We create a
new inspection, selecting a relationship with the model (sale, stock move...),
and pressing "Select test" button to choose the test to pass. Then, you must
fill the lines depending on the chosen test.

The complete inspection workflow is:

    Draft -> Confirmed -> Success
                |
                | -> Failure (Pending approval) -> Approved

Based on the nan_quality_control_* modules from NaN·tic.


Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/129/11.0


Known issues / Roadmap
======================

* Make translatable the trigger name.


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
* Pedro M. Baeza <pedro.baeza@serviciobaeza.com>
* Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>
* Ana Juaristi <anajuaristi@avanzosc.es>
* Lois Rilo <lois.rilo@eficent.com>
* Simone Rubino <simone.rubino@agilebg.com>
* Juan Humanes <juan.humanes@guadaltech.es>

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
