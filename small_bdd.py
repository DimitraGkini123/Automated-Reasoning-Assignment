from oxidd.bdd import BDDManager

mgr = BDDManager(100_000_000, 1_000_000, 1)

levels = mgr.add_vars(3)
x = [mgr.var(i) for i in levels]

# φ = (x1 OR NOT x2) AND (x2 OR x3)

c1 = x[0] | ~x[1]
c2 = x[1] | x[2]

f = c1 & c2

mgr.visualize_with_names(
    "example",
    [
        (c1, "clause1"),
        (c2, "clause2"),
        (f, "phi")
    ]
)