# contract-allocation

![WebUI](https://img.shields.io/badge/UI-WebUI-success)

**Mirrored in:** https://github.com/aimms/contract-allocation

**How-to:** https://how-to.aimms.com/Articles/383/383-contract-allocation.html

## Problem Description

In this model we have a set of contracts, where every contract represents an amount of commodity that has to be supplied. The objective is to determine which of the producers will take care of which contract such that the total costs are minimal, under the following conditions:


- The demand for every contract is met.

- The amount supplied by each producer does not exceed the total amount available for supply.

- If a producer supplies a part of a contract then this contribution has a given minimal size.

- There is a minimal number of suppliers for every contract. 

- The total cost associated with all the deliveries is minimal.