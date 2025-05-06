While associating a standard safety symbol (e.g., M016 "Wear respiratory protection") with a Work Center is useful (via `mrp_workcenter_safety_symbol`), it often lacks necessary detail for practical implementation. The specific *type* of respirator (e.g., P2, P3 filter), the required maintenance schedule, or other crucial instructions related to that safety requirement might vary depending on the exact task or substances present at that Work Center.

The business need is to capture these specific instructions or qualifications directly alongside the general symbol for a given Work Center, ensuring operators have precise, actionable safety information.

*Example Use Case:* For Work Center "Paint Booth", the symbol M016 "Wear respiratory protection" is selected. However, the specific requirement is an "Organic Vapor Cartridge, replace weekly". This module allows adding this text note directly linked to the M016 symbol specifically for the "Paint Booth" Work Center.
