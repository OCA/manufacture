.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================================
Manufacturing Operations Extension
==================================

This module adds:

* New table to store operations to avoid typing them again.
* Adds a relation from workcenter lines to Bill of Materials (BoM) lists.
* Adds a relation between workcenter lines and Manufacturing Orders in
  Scheduled/Consumed/Finished products.
* Adds a relation between workcenter lines and BoM lists.
* Allows to set specific times per routing in addition to workcenter times.
* Controls the availability of material in operations
* Controls operation beginning in previous operations are not finished.

Installation
============

Once the module is installed, it transforms all existing routings to:

* Mark the last operation as the one where the production is done.
* Create a workcenter routing line (new model for allowing more than one
  workcenter per operation) for the current selected workcenter.

Configuration
=============

Go to *Settings > Manufacturing* and activate "Manage routings and work orders"
for handling the features of this module.
Go to *Settings > Manufacturing* and deactivate "Compute Cycles by BoM Quantity"
in order to compute cycles without BoM product quantity.

Usage
=====

You can go to *Manufacturing > Configuration > Operations* to add templates
of the operations you do on your manufacturing process defining:

* Possible workcenters to use.
* Number of operators involved.
* Extended description.

This operation template can then be selected when you create routing lines
in *Manufacturing > Products > Routings* as the default initial data for that
line.

In this screen, you are now allowed to put more than one possible work
centers, and you can also select if the capacity data of the work center
is specific for that route or the general one.

You can also define here in which of the lines the production is going to be
made, in order to prevent to do it before reaching this operation. This is done
marking the check "Produce here" in the routing line.

One last possibility for the routing lines is to set if you require to finish
previous operations before allowing to start this one, which is done marking
the check "Previous operations finished".

Once defined the routing, you can select the routing on your BoMs, going to
*Manufacturing > Products > Bill of Materials*, and select for each component
in which routing operation you are going to consume the material.

Finally, having all set, we can create a manufacturing order with a BoM and
a routing selected. Clicking on "Compute Data" button on "Work Orders" or
"Scheduled Products" tab, we will preview which work orders and products we
will need for this manufacturing.

Clicking on a work order line, we can see in detail the times involved for that
operation and the raw materials that are going to be consumed on it.

We can start the manufacturing process clicking on "Confirm Production" button.
Then, we can control each operation start from the "Work Orders" tab of the
manufacturing order, or go to *Manufacturing > Manufacturing > Work Orders*
to see them directly. We will only be allowed to consume the materials that
has been assigned to the corresponding work order, and to produce when the
operation with the "Produce here" flag is set.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/129/8.0

Known issues
============

* *hr_timesheet* is a big dependency for only catching the employee cost when
  selecting operators in the workcenter. A glue module for this operation
  would be desired.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/manufacture/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
manufacture/issues/new?body=module:%20
mrp_operations_extension%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Daniel Campos <danielcampos@avanzosc.es>
* Mikel Arregi <mikelarregi@avanzosc.es>
* Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>
* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
* Ana Juaristi <anajuaristi@avanzosc.es>
* Rafael Blasco <rafabn@antiun.com>

Images
------

* Original Odoo MRP icon
* Thanks to https://openclipart.org/detail/151831/work-bench

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
