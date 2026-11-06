In standard Odoo, the quantity of a byproduct on a manufacturing order is
recomputed from the producing quantity whenever it is (re)evaluated, including
when *Produce All* fills the producing quantity automatically. As a result, a
quantity that an operator entered manually on a byproduct line is silently
reset to the quantity to produce, unless the line happens to be marked as
picked.

This module adds an *Auto-pick Manually Edited Byproducts* option to
manufacturing orders (defaulted from a company-wide setting) to keep the
manually entered byproduct quantity: when an operator edits the quantity of a
byproduct line on an enabled manufacturing order, the line is automatically
marked as picked so its value is preserved through *Produce All*.

Byproduct lines that are not edited keep the standard behavior and still scale
with the producing quantity.
