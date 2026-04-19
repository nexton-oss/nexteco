# Examples

## Example 1: API-heavy repository

Canonical unit of work:
- one representative request that invokes a paid model API

Focus:
- runtime
- token or call-based API spend
- local orchestration cost
- total cost split

## Example 2: Local-compute repository

Canonical unit of work:
- one local inference or batch execution

Focus:
- runtime
- estimated or measured power draw
- electricity cost
- carbon intensity assumptions

## Example 3: Mixed system

Canonical unit of work:
- one request path with both local compute and external APIs

Focus:
- keep the split visible
- avoid flattening unlike costs too early
