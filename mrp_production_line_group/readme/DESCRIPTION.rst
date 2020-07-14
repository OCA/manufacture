When you have a BOM with many sub-BOM it is possible that a product is present in many of this.
When a MO is created, each sub-BOM of type phantom is exploded adding all products in the MO sequentially.
So the result is that the same product can be repeated in many rows, which can be misleading to the user.

This module add a button which unify the lines with the same product coming from phantom BOM. When this function is used, it is not possible to change the quantity manufactured anymore, as the single line cannot be linked to many bom lines which the initial ones where linked, so the button 'Update' quantity manufactured become invisible.
