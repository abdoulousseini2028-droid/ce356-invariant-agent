---- MODULE MutualExclusion ----
EXTENDS Naturals, TLC

VARIABLES pc1, pc2
vars == <<pc1, pc2>>

Init == pc1 = "idle" /\ pc2 = "idle"

Request1 == pc1 = "idle"     /\ pc1' = "waiting"  /\ UNCHANGED pc2
Enter1   == pc1 = "waiting"  /\ pc2 # "critical"  /\ pc1' = "critical" /\ UNCHANGED pc2
Exit1    == pc1 = "critical" /\ pc1' = "idle"      /\ UNCHANGED pc2

Request2 == pc2 = "idle"     /\ pc2' = "waiting"  /\ UNCHANGED pc1
Enter2   == pc2 = "waiting"  /\ pc1 # "critical"  /\ pc2' = "critical" /\ UNCHANGED pc1
Exit2    == pc2 = "critical" /\ pc2' = "idle"      /\ UNCHANGED pc1

Next == Request1 \/ Enter1 \/ Exit1 \/ Request2 \/ Enter2 \/ Exit2
Spec == Init /\ [][Next]_vars /\ WF_vars(Next)

MutualExclusion == ~(pc1 = "critical" /\ pc2 = "critical")
Liveness1 == (pc1 = "waiting") ~> (pc1 = "critical")
Liveness2 == (pc2 = "waiting") ~> (pc2 = "critical")

THEOREM Spec => []MutualExclusion
====
