# ShortParse Mechanic Failure Types

## avoidable_damage
Use when getting hit is bad.

Examples:
- Swirl
- Frontal
- Ground puddle
- Avoidable projectile

Failure condition:
- Player took damage from the tracked spell.

---

## missed_interrupt
Use when an enemy cast should have been stopped.

Examples:
- Add casts Shadow Fracture
- Enemy casts raid-wide heal
- Enemy casts buff/debuff spell

Failure condition:
- A tracked cast event completed.

Important:
- This is not damage-based.
- The failure is the completed cast.

---

## required_soak
Use when players are supposed to take damage.

Examples:
- Everyone must soak a pulse
- Assigned players must stand in circles
- Group soak mechanics

Failure condition:
- Eligible player did not take the tracked soak damage.

Important:
- This is the inverse of avoidable damage.

---

## bad_soak
Use when taking the soak is bad for certain players.

Examples:
- Player has vulnerability debuff
- Player already soaked recently
- Wrong role soaked
- Tank-only soak hit non-tank

Failure condition:
- Player took soak damage while ineligible.

---

## missed_dispel
Use when a debuff should be removed.

Failure condition:
- Debuff lasted too long.
- Debuff expired naturally when it should have been dispelled.

---

## bad_dispel
Use when dispelling is dangerous unless timed correctly.

Failure condition:
- Debuff was dispelled too early.
- Debuff was dispelled during the wrong phase/window.

---

## spread_failure
Use when too many players are hit by a mechanic that should be isolated.

Failure condition:
- More than the allowed number of players were hit within a short time window.

---

## stack_failure
Use when too few players share a mechanic.

Failure condition:
- Fewer than the required number of players were hit by the soak/share spell.

---

## tank_hit
Use for tank-buster or tank assignment mechanics.

Failure condition depends on the mechanic:
- wrong role hit
- same tank hit too many times
- tank hit with too many stacks