This module adds a new `mrp.unbuild.rebuild.variant` which acts as a wrapper around the unbuilding - rebuilding process of different variants.

This is quite useful as it ensures the same tracked components will be used in the rebuilding process.

Warning:

* Your components are not tracked by SN, you can use the module straight away
* Your components are tracked by SN, you need to manually unbuild and launch a MO (because you cannot decide with lot/SN you remove)
