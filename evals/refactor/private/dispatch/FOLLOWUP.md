Add a fragile-item restriction: express shipping is unavailable for any order
containing an item with fragile=True when total order weight exceeds 10000 grams.
Use reason express_fragile_weight and the usual rejection shape. This new rule
comes after all existing rejection rules. Standard shipping and express orders
of exactly 10000 grams stay unchanged. Add focused tests and implement it.
