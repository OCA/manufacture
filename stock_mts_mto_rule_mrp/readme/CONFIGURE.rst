To use the MTS + MTO rules for manufacturing on a warehouse:

1. configure the warehouse to use "Pick components and then manufacture (2 steps)"
2. Find the route "Pick components and then manufacture" of the
   warehouse. There should be 2 rules: one to pull products from Stock and
   bring it to PreProduction (using MTS), and one to pull products from
   PreProduction and to bring it to Production (MTO). You need to create 2 new
   rules:

   * one route to pull products from PreProduction and bring it to Production (MTS), using the Manufacturing operation type
   * one route to choose between MTS and MTO, with Operation Type:
     Manufacturing, Source location PreProduction, Destination Production, MTS
     rule: the one created in the previous step, MTO rule: the preexisting MTO
     rule pulling from PreProduction to Production
