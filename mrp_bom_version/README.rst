.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================
MRP - BoM Version
=================

This module provides a state in the BoM whether to allow their use in
manufacturing.


Usage
=====

The following states are defined:

* **Draft**:
  The form will be available for data entry, and may move to "active" state.
* **Active**:
  You can modify all of the form fields except for the fields: routing, BoM
  lines, and the new field Active, for false default when you create a new BoM.
  The "active" state may be passed back to state "draft", if we mark the new
  field "Allow re-edit the BoM list", this new field is defined in 
  *Configuration > Configuration > Manufacturing*. You can configure there also
  if those BoM will continue with active check marked as True or not.
  The active state may move to state "Historical".
* **Historical**: 
  This is the last state of the LdM, you can not change any field on the form.

When the MRP BoM list is put to active, a record of who has activated, and when
will include in chatter/log. It also adds a constraint for the sequence field
to be unique.

* **New version** :
  By clicking the button version, current BOM is moved to historical state,
  and a new BOM is creating based on this but with version number +1 and
  changing state to draft


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/avanzosc/mrp-addons/issues>`_. In case of trouble,
please check there if your issue has already been reported. If you spotted
it first, help us smash it by providing detailed and welcomed feedback.

Do not contact contributors directly about support or help with technical issues.


Credits
=======

Contributors
------------
* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
* Ana Juaristi <anajuaristi@avanzosc.es>
* Alfredo de la Fuente <alfredodelafuente@avanzosc.es>
* Oihane Crucelaegui <oihanecrucelaegui@avanzosc.es>
