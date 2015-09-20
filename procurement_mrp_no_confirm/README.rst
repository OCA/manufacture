Don't confirm MOs when procured
===============================

This module prevents the automatic confirmation of manufacturing order when
procurement orders are executed.

Known issues / Roadmap
======================

* If the production order workflow has been altered in the transition
  *prod_trans_draft_picking* to have another condition, when uninstalling this
  module, you will need to restore the custom condition.
