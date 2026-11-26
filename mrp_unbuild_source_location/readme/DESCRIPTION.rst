This module filters the source location on an unbuild order to only locations where the
product currently has positive stock. When a lot/serial number is specified, the filter
is further narrowed to locations holding that specific lot.

If stock exists in a single location, it is automatically set as the source location. If
stock exists in multiple locations, the list is narrowed down for the user to choose
from.

Consider using this module alongside ``stock_no_negative`` to prevent unbuild orders
from driving stock negative at the selected location.
