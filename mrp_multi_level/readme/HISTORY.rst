13.0.1.3.0 (2020-03-02)
~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Minor changes"
  (`#470 <https://github.com/OCA/manufacture/pull/470>`_).

  * Planned Order release and due date become required.
  * Add button to Product MRP Area to update MOQ from Supplier Info.
  * Link Manufacturing Orders with Planned Orders.
  * Allow Mrp Inventory Procure Wizard to be used from other models.
  * Make MRP Inventory creation more extensible.
  * Main Supplier computation (v13 requires explicit False definitions)

13.0.1.2.0 (2020-02-20)
~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Minor changes
  (`#468 <https://github.com/OCA/manufacture/pull/468>`_).

  * Planned Orders become fixed on manual creation by default
  * Released Quantity becomes readonly
  * Add product reference if Planned Order name is not defined on bom explosion

13.0.1.1.0 (2020-02-21)
~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] Minor changes
  (`#469 <https://github.com/OCA/manufacture/pull/469>`_).

  * Fix Main supplier computation in multi company
  * Drop Triplicated field in search view


* [IMP] Minor changes
  (`#463 <https://github.com/OCA/manufacture/pull/463>`_).

  * Show supply method on MRP Inventory
  * Allow no-MRP users to look into Products

13.0.1.0.0 (2019-12-18)
~~~~~~~~~~~~~~~~~~~~~~~

* [MIG] Migration to v13.

12.0.1.0.0 (2019-08-05)
~~~~~~~~~~~~~~~~~~~~~~~

* [MIG] Migration to v12:

  * Estimates as a forecasting mechanism is moved to a new module
    (mrp_multi_level_estimate).

11.0.3.0.0 (2019-05-22)
~~~~~~~~~~~~~~~~~~~~~~~

* [REW/IMP] Rework to include Planned Orders.
  (`#365 <https://github.com/OCA/manufacture/pull/365>`_).
* [IMP] Able to procure from a different location than the area's location.

11.0.2.2.0 (2019-05-02)
~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Able to run MRP only for selected areas.
  (`#360 <https://github.com/OCA/manufacture/pull/360>`_).

11.0.2.1.0 (2019-04-02)
~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Implement *Nbr. Days* functionality to be able to group demand when
  generating supply proposals.
  (`#345 <https://github.com/OCA/manufacture/pull/345>`_).

11.0.2.0.0 (2018-11-20)
~~~~~~~~~~~~~~~~~~~~~~~

* [REW] Refactor MRP Area.
  (`#322 <https://github.com/OCA/manufacture/pull/322>`_):

  * MRP product concept dropped in favor of *Product MRP Area Parameters*.
    This allow to set different MRP parameters for the same product in
    different areas.
  * Menu items reordering.

11.0.1.1.0 (2018-08-30)
~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] Consider *Qty Multiple* on product to propose the quantity to procure.
  (`#297 <https://github.com/OCA/manufacture/pull/297>`_)

11.0.1.0.1 (2018-08-03)
~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] User and system locales doesn't break MRP calculation.
  (`#290 <https://github.com/OCA/manufacture/pull/290>`_)
* [FIX] Working Hours are now defined only at Warehouse level and displayed
  as a related on MRP Areas.
  (`#290 <https://github.com/OCA/manufacture/pull/290>`__)

11.0.1.0.0 (2018-07-09)
~~~~~~~~~~~~~~~~~~~~~~~

* Start of the history.
