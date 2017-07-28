.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=====================
Quality Control Issue
=====================

This module extends the functionality of quality Control to allow you to
report and manage quality control issues.

Configuration
=============

To configure this module in order to take advantage of the kanban views you
need to create the stages for *issues* and *problems*. To **create** stages in
any kanban view click on *Add New Column*. Then you can **reorder** the stages
just dragging them.

In created stages you can **configure** them clicking on the gear button that
appears at the right of the stage name and clicking on *Edit*. Note the
following behaviors:

* You can set a *Quality Control Team*.

  - Stages with no team set will be shared by all teams.
  - Stages with a team associated will be only available for that specific
    team.

* In Issue Stages you can also relate a *QC State* to the stage.

  - When you move to a different stage an issue with *QC state* defined the
    state of the issue will also change according to it.
  - The other way around, if you change the state, the system will look for
    an appropriate stage and if existing the issue will be move to that stage.
  - If you change the *QC team* of an issue, the system will get the default
    stage for that team and apply it to the issue.

Usage
=====

To use Quality Control Issues, you need to:

#. Go to *Quality Control > Issues > QC Issues* or to *Quality Control >
   Dashboard* and click on *Issues* in any of your teams.
#. Click on create to report an issue.
#. Select the product and quantity for the issue. Optionally you can specify
   a location and relate the issue to some *Problem*.

To manage your Quality Control Problems, you have to:

#. Go to *Quality Control > Problem Tracking > Problems* or to *Quality
   Control > Dashboard* and click on *Problems* in any of your teams.

Issue Dispositions:
-------------------

You can perform the following actions in quality control issues 'in progress':

* Scrap: Click on *Scrap Products* button.
* Create RMA: Install `rma_quality_control_issue` and see instructions there.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/129/9.0

Known issues / Roadmap
======================

Todo:
-----

* Add more dispositions: repair, refurbish...

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

* Lois Rilo <lois.rilo@eficent.com>
* Jordi Ballester Alomar <jordi.ballester@eficent.com>

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
