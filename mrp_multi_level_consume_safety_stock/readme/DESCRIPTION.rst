This module complements the `mrp_multi_level` module by allowing to set a date 
on the mrp.area records until which no attempt to rebuild safety stock will be 
attempted: the safety stock will be used, if the running stock get below zero, 
then a resupply will be created to bring back the stock to zero. 

The idea is that your area may be under tension at a given moment (maybe
some workers are off, maybe there is high demand from customers) and you
can barely keep up with the demand. In this case, you can set
Safety stock rebuild lead date to a date in the future at
which you anticipate that the situation will have been fixed.
