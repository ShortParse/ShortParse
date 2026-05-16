# ShortParse Mechanic Decision Matrix

This document helps contributors choose the correct `failure_type`, `category`, and tracking approach when adding boss mechanics.

The goal is consistency.

ShortParse separates two ideas:

```text
failure_type = how the engine detects the failure
category     = what kind of mechanic it is
```

Example:

```python
"category": "ground_effect",
"failure_type": "avoidable_damage",
```

That means:

```text
The mechanic is a ground effect.
The failure is that the player took avoidable damage.
```

---

# Fast Rule

If you are not sure what to use, answer this question first:

```text
What does failure mean?
```

Then use the table below.

---

# Decision Matrix

| Question | Failure means... | Use `failure_type` | Good `category` examples | Example mechanic |
|---|---|---|---|---|
| Did a player get hit by something they should avoid? | Player took avoidable damage | `avoidable_damage` | `ground_effect`, `traveling_projectile`, `frontal`, `rear_cone`, `beam`, `swirl`, `movement` | Void Fall, Oblivion's Wrath, Tail Lash |
| Did an enemy cast finish when it should have been stopped? | Cast completed | `missed_interrupt` | `interrupt` | Shadow Fracture |
| Did too few players soak a mechanic? | Soak count was below requirement | `minimum_soak` | `minimum_soak`, `group_soak`, `orb_soak` | Gloom requires 5 players |
| Did a player never participate in a required mechanic? | Player had 0 participation | `zero_participation` | `soak_participation`, `interrupt_participation`, `add_priority` | Jimmy had 0 Gloom touches |
| Did a player soak while they should not have? | Ineligible player soaked | `bad_soak` | `bad_soak`, `vulnerability`, `wrong_assignment` | Player soaked while debuffed |
| Did a debuff stay on too long? | Dispel was missed or late | `missed_dispel` | `dispel`, `curse`, `magic`, `poison`, `disease` | Black Miasma not removed |
| Was a debuff dispelled at the wrong time? | Dispel timing was bad | `bad_dispel` | `bad_dispel`, `explosive_dispel` | Dispel exploded in raid |
| Did too many players get hit by a spread mechanic? | Players were too close | `spread_failure` | `spread`, `splash`, `chain` | Player circles overlapped |
| Did too few players stack/share damage? | Stack group too small | `stack_failure` | `stack`, `shared_damage`, `group_soak` | Shared soak missed |
| Did a non-tank take boss/tank damage? | Wrong role/player was hit | `avoidable_damage` for now, later `tank_hit` | `boss_threat`, `tank_buster` | Non-tank hit by boss primary attack |
| Did an add live too long or cast too often? | Raid failed add management | `add_management` later, or `missed_interrupt`/`avoidable_damage` if tied to specific events | `add_priority`, `add_management` | Add applied repeated raid damage |
| Did a player fail an assignment? | Assigned player did not perform task | `assignment_failure` later | `assignment`, `soak_assignment`, `bomb_assignment` | Assigned soaker missed orb |
| Did a player fail to use a defensive? | Player took lethal/high damage without defensive | `missed_defensive` later | `defensive`, `survivability` | Player died without available defensive |
| Did a tank fail a swap/stack rule? | Tank had too many stacks or wrong tank was hit | `tank_swap_failure` later | `tank_swap`, `tank_buster` | Same tank took repeated busters |
| Did a player drop/bait something badly? | Placement was harmful | `bad_placement` later | `bait`, `drop_location`, `puddle_drop` | Puddle dropped in raid path |

---

# Failure Type Guide

## `avoidable_damage`

Use when:

```text
A player took damage from something they should have avoided.
```

Common categories:

```text
ground_effect
traveling_projectile
frontal
rear_cone
beam
swirl
movement
forced_movement
lane_movement
debuff_damage
boss_threat
```

Good examples:

```python
VOID_FALL: Mechanic = {
    "category": "ground_effect",
    "failure_type": "avoidable_damage",
}
```

```python
OBLIVIONS_WRATH: Mechanic = {
    "category": "traveling_projectile",
    "failure_type": "avoidable_damage",
}
```

```python
TAIL_LASH = {
    "category": "rear_cone",
    "failure_type": "avoidable_damage",
}
```

Do not use this for unavoidable raid-wide damage.

---

## `missed_interrupt`

Use when:

```text
An enemy cast completed and should have been interrupted.
```

This uses cast events, not damage events.

Good example:

```python
SHADOW_FRACTURE: Mechanic = {
    "category": "interrupt",
    "failure_type": "missed_interrupt",
    "wcl_type": "cast",
}
```

Use the cast spell ID.

Do not use the later damage spell ID unless the cast event is unavailable.

---

## `minimum_soak`

Use when:

```text
A soak event required at least X players, but fewer than X players soaked it.
```

This is usually a raid/group failure.

Good example:

```python
GLOOM_MINIMUM_SOAK: Mechanic = {
    "category": "minimum_soak",
    "failure_type": "minimum_soak",
    "minimum_soakers": 5,
    "spell_ids": [1245500],
}
```

Use this for:

```text
At least 5 people must soak.
At least 3 people must split the damage.
Group soak failed because too few players stood in it.
```

Do not use this to ask whether Jimmy personally soaked. Use `zero_participation` for that.

---

## `zero_participation`

Use when:

```text
A player had zero involvement in a mechanic they were expected to help with.
```

Good example:

```python
GLOOM_PARTICIPATION: Mechanic = {
    "category": "soak_participation",
    "failure_type": "zero_participation",
    "spell_ids": [1245500],
}
```

Use this for questions like:

```text
Did Jimmy never touch Gloom?
Did a DPS never swap to adds?
Did a player never interrupt?
Did a healer never dispel?
```

This is accountability tracking, not event failure tracking.

---

## `bad_soak`

Use when:

```text
A player soaked when they should not have.
```

Good example:

```python
BAD_GLOOM_SOAK = {
    "category": "bad_soak",
    "failure_type": "bad_soak",
    "spell_ids": [1245500],
    "bad_soak_if_aura_ids": [999999],
}
```

Use this for:

```text
Player had vulnerability debuff and soaked anyway.
Player already soaked recently and soaked again.
Wrong role soaked.
Unassigned player soaked.
```

---

## `missed_dispel`

Use when:

```text
A debuff was not removed, or was removed too late.
```

Good example:

```python
BLACK_MIASMA = {
    "category": "dispel",
    "failure_type": "missed_dispel",
    "spell_ids": [1275059],
}
```

Use this when the failure is the debuff lasting too long.

If you are only tracking damage ticks for now, use:

```python
"failure_type": "avoidable_damage"
"category": "debuff_damage"
```

until true dispel logic exists.

---

## `bad_dispel`

Use when:

```text
A debuff was dispelled at the wrong time or in the wrong location.
```

Use this for:

```text
Early dispel caused raid damage.
Dispel happened before player moved out.
Dispel happened during a dangerous overlap.
Wrong target was dispelled first.
```

---

## `spread_failure`

Use when:

```text
Too many players were hit by a mechanic that should have been isolated.
```

Use this for:

```text
Splash damage from players standing too close.
Chain lightning jumped to too many players.
Circle overlap hit multiple players.
```

---

## `stack_failure`

Use when:

```text
Too few players stacked/shared damage.
```

Use this for:

```text
Shared damage had too few players.
Stack marker was not soaked by enough people.
Group did not collapse for split damage.
```

This is similar to `minimum_soak`, but use:

```text
minimum_soak = soak orb/circle needs X bodies
stack_failure = stack/share mechanic needs X bodies
```

When unsure, use `minimum_soak` for soak-specific mechanics.

---

## `lane_movement`

Use this category when:

```text
Players must avoid marching adds, lane sweeps, or moving lane-based hazards.
```

Good examples:

```text
Marching add lanes
Boss army crossing the room
Moving wall/lane hazard
Lane sweep that kills players on contact
```

Use with:

```python
"category": "lane_movement",
"failure_type": "avoidable_damage",
```

---

## `debuff_damage`

Use this category when:

```text
The current engine is tracking damage ticks from a debuff, not true dispel timing.
```

Good examples:

```text
Curse tick damage
Magic debuff tick damage
DoT damage from a removable mechanic
Damage taken because a debuff remained active
```

Use with:

```python
"category": "debuff_damage",
"failure_type": "avoidable_damage",
```

Later, when aura duration, dispel timing, and actual dispel events are supported, some `debuff_damage` mechanics may become:

```python
"failure_type": "missed_dispel"
```

---

# Category Guide

Categories should be lowercase snake_case.

Good categories:

```text
ground_effect
traveling_projectile
frontal
rear_cone
beam
swirl
movement
interrupt
minimum_soak
soak_participation
bad_soak
dispel
spread
stack
boss_threat
tank_buster
tank_swap
add_management
add_priority
bait
drop_location
defensive
survivability
```

Bad categories:

```text
Ground Effect
Bad Stuff
Avoid
Mechanic
Misc
Dodge Things
```

---

# Severity Guide

## Info

Use for low-impact tracking.

Examples:

```text
Minor add damage
Low-value uptime pressure
Interesting but not severe
```

## Warning

Use for moderate issues or repeated small mistakes.

Examples:

```text
Projectile hits
Low participation
Minor movement mistakes
```

## Major

Use for mechanics that strongly affect progression.

Examples:

```text
Missed interrupt
High avoidable damage
Spread failure
Important dispel issue
```

## Critical

Use for mechanics that can kill players, wipe the raid, or block progression.

Examples:

```text
One-shot mechanics
Required soak failures
Tank-buster failures
Lethal ground effects
Major soak failures
```

---

# Tracking Rules

## Track the failure event

Many mechanics have multiple spell IDs:

```text
cast ID
damage ID
debuff ID
visual ID
missile ID
trigger ID
```

Pick the ID that best represents the failure.

Examples:

```text
Avoidable damage mechanic:
Track damage ID.

Missed interrupt:
Track cast ID.

Missed dispel:
Track aura/debuff ID or expiry/removal events.

Minimum soak:
Track soak damage ID.

Zero participation:
Track participation/touch/damage ID.
```

---

# When NOT to Track

Do not track:

```text
Passive raid-wide damage
Normal tank melee
Player self-damage
Friendly cooldown side-effects
Class ability self-damage
Unavoidable boss aura ticks
Background environmental effects everyone must take
```

Unless the mechanic is specifically about mitigating, dispelling, soaking, or surviving that damage.

---

# Typed Mechanic Definitions

Encounter mechanics should use the shared `Mechanic` type:

```python
from shortparse.data.encounters.types import Mechanic
```

Good:

```python
VOID_FALL: Mechanic = {
    "name": "Void Fall",
    "category": "swirl",
    "failure_type": "avoidable_damage",
}
```

This improves PyCharm autocomplete and makes invalid `category` or `failure_type` strings easier to catch.

The spell mapping does not change:

```python
**mechanic_aliases(
    [1258883],
    VOID_FALL,
),
```

---

# Standard Mechanic Template

```python
MECHANIC_CONSTANT: Mechanic = {
    "name": "Display Name",

    "severity": "Major",
    "avoidable": True,

    "category": "category_here",
    "failure_type": "failure_type_here",

    "counts_as_failure": True,

    "max_reasonable_hits": 1,
    "score_per_hit": 50,

    "applies_to": ALL_ROLES,

    "note": (
        "Explain what happens."
    ),

    "recommendation": (
        "Explain what players should do."
    ),

    "wcl_type": "damage_taken",
}
```

---

# Examples

## Ground Effect

```python
VOID_FALL: Mechanic = {
    "name": "Void Fall",
    "severity": "Critical",
    "avoidable": True,
    "category": "ground_effect",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": (
        "Adds launch void energy into the air, creating a ground impact circle."
    ),
    "recommendation": (
        "Move out of the impact circle before it lands."
    ),
    "wcl_type": "damage_taken",
}
```

## Traveling Projectile

```python
OBLIVIONS_WRATH: Mechanic = {
    "name": "Oblivion's Wrath",
    "severity": "Warning",
    "avoidable": True,
    "category": "traveling_projectile",
    "failure_type": "avoidable_damage",
    "counts_as_failure": True,
    "max_reasonable_hits": 4,
    "score_per_hit": 20,
    "applies_to": ALL_ROLES,
    "note": (
        "Void projectiles travel outward from the boss, damaging and knocking back players hit."
    ),
    "recommendation": (
        "Avoid the outward-moving projectiles."
    ),
    "wcl_type": "damage_taken",
}
```

## Missed Interrupt

```python
SHADOW_FRACTURE: Mechanic = {
    "name": "Shadow Fracture",
    "severity": "Major",
    "avoidable": True,
    "category": "interrupt",
    "failure_type": "missed_interrupt",
    "counts_as_failure": True,
    "max_reasonable_hits": 4,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": (
        "Adds cast Shadow Fracture, which should be interrupted."
    ),
    "recommendation": (
        "Interrupt Shadow Fracture casts before they complete."
    ),
    "wcl_type": "cast",
}
```

## Minimum Soak

```python
GLOOM_MINIMUM_SOAK: Mechanic = {
    "name": "Gloom",
    "severity": "Critical",
    "avoidable": False,
    "category": "minimum_soak",
    "failure_type": "minimum_soak",
    "counts_as_failure": True,
    "minimum_soakers": 5,
    "max_reasonable_hits": 0,
    "score_per_hit": 100,
    "applies_to": ALL_ROLES,
    "spell_ids": [1245500],
    "note": (
        "Gloom requires at least 5 players to soak each orb."
    ),
    "recommendation": (
        "Assign soak groups and make sure at least 5 eligible players touch each orb."
    ),
    "wcl_type": "damage_taken",
}
```

## Zero Participation

```python
GLOOM_PARTICIPATION: Mechanic = {
    "name": "Gloom Participation",
    "severity": "Warning",
    "avoidable": False,
    "category": "soak_participation",
    "failure_type": "zero_participation",
    "counts_as_failure": True,
    "max_reasonable_hits": 0,
    "score_per_hit": 50,
    "applies_to": ALL_ROLES,
    "spell_ids": [1245500],
    "note": (
        "Tracks players who had zero Gloom soak participation."
    ),
    "recommendation": (
        "Review players with 0 Gloom touches to confirm assignments and participation."
    ),
    "wcl_type": "damage_taken",
}
```

---

# Contributor Checklist

Before submitting a mechanic:

```text
[ ] Spell ID is confirmed from Warcraft Logs.
[ ] Spell ID represents the failure event.
[ ] Unavoidable damage is excluded.
[ ] Player/class self-damage is excluded.
[ ] failure_type describes engine behavior.
[ ] category describes mechanic identity.
[ ] Severity matches progression impact.
[ ] Note explains what happens.
[ ] Recommendation tells players what to do.
[ ] max_reasonable_hits is reasonable.
[ ] score_per_hit is reasonable.
[ ] applies_to is correct.
[ ] Mechanic was tested against at least one real report.
```

---

# If Unsure

Do not invent a new `failure_type` casually.

Use this process:

```text
1. Can the current engine detect this?
2. Is this player-level, group-level, or raid-level?
3. Is the failure damage, cast completion, missed participation, missed soak, bad soak, or dispel timing?
4. If none fit, propose a new failure_type and document it.
```
