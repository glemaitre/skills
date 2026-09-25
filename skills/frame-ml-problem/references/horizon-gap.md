# Horizon and gap

Record both, with the same unit. They are equal only when nothing
arrives later than the label overlap.

**Horizon** is how far ahead the target sits. It defines the value
at `t + h`, and it is the shortest overlap that must be embargoed
so a training label does not fall inside the period being scored.

**Gap** is the extra delay before a forecast can be issued in
deployment: features or labels that are not available yet. If data
arrives late, the gap is longer than the horizon. A gap shorter
than the horizon, in the same unit, leaves that overlap in the
training window.

Write `<number> <unit>`, for example `7 day`. Do not name a
splitter class or a constructor argument.
