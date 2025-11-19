This module defines triggers that creates inspections when stock moves are done.

It also adds some shortcuts on picking and lots to these inspections.
Activating the "Remind Quality Control" flag on products, if inspections are not done (successfully or unsuccessfully), on picking confirmation a reminder popup appears.
Activating "Scrap Automatically" flag on products, if inspections fail, picking:
- Will be automatic validated if every product in picking has the flag checked;
- On validation, will generate scraps automatically for every product with the flag checked and whose inspection has failed;
Activating "Create Nonconformity" flag on products, for every failed inspection, a new Nonconformity will be opened.
