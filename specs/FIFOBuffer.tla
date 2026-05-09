---- MODULE FIFOBuffer ----
EXTENDS Sequences, Naturals, TLC

CONSTANT Capacity
ASSUME Capacity \in Nat /\ Capacity > 0

VARIABLES buffer, produced, consumed
vars == <<buffer, produced, consumed>>

Init == /\ buffer = <<>> /\ produced = 0 /\ consumed = 0

Produce(val) == /\ Len(buffer) < Capacity /\ buffer' = Append(buffer, val)
                /\ produced' = produced + 1 /\ UNCHANGED consumed

Consume == /\ Len(buffer) > 0 /\ buffer' = Tail(buffer)
           /\ consumed' = consumed + 1 /\ UNCHANGED produced

Next == (\E val \in 1..100 : Produce(val)) \/ Consume
Spec == Init /\ [][Next]_vars

NoOverflow    == Len(buffer) <= Capacity
ConsistentCount == consumed <= produced

THEOREM Spec => []NoOverflow
THEOREM Spec => []ConsistentCount
====
