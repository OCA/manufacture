This module extends the functionality of Manufacturing to support the creation
of procurements only for a part of the raw material.
It has 2 modes. The default one allow you to pull
from stock until the quantity on hand is zero, and then create a procurement
to fulfill the MO requirements. In this mode, the created procurements must
be the ones fulfilling the MO that has generated it.
The other mode is based on the forecast quantity. It will allow to pull from
stock until the forecast quantity is zero and then create a procurement for
the missing products. In this mode, there is no link between the procurement
created and MO that has generated it. The procurement may be used to fulfill
another MO.