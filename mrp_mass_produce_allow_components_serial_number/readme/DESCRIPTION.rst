Simple module that modify standard method `_check_serial_mass_produce_components`
in order to allow to mass product a finished product that contains components
that are tracked by SN (and not by lot).

Warning: This module breaks inheritance on the method `_split_productions` to
be able to manage components managed by S/N
