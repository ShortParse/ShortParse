# ShortParse Mechanic Builder

Use this document to build consistent boss mechanic definitions for ShortParse.

Goal:

1. Identify what happened.
2. Decide what failure means.
3. Choose the correct `failure_type`.
4. Choose a clear `category`.
5. Generate a clean Python mechanic block.
6. Add the spell ID mapping with `mechanic_aliases()`.

---

# Quick Decision Matrix

| What happened? | Failure means... | Use `failure_type` | Example `category` |
|---|---|---|---|
| Player got hit by something avoidable | Player took avoidable damage | `avoidable_damage` | `ground_effect`, `traveling_projectile`, `frontal`, `rear_cone`, `swirl`, `beam`, `movement` |
| Enemy cast completed | Cast should have been interrupted | `missed_interrupt` | `interrupt` |
| Too few players soaked | Group failed minimum soak requirement | `minimum_soak` | `soak`, `orb_soak`, `group_soak` |
| Player never touched/handled mechanic | Player did not participate | `zero_participation` | `soak_participation`, `interrupt_participation`, `add_priority` |
| Player soaked while ineligible | Wrong player soaked | `bad_soak` | `soak`, `vulnerability`, `wrong_assignment` |
| Debuff was not removed in time | Dispel was missed or late | `missed_dispel` | `dispel`, `curse`, `magic`, `poison`, `disease` |
| Debuff was removed at the wrong time | Bad/early/unsafe dispel | `bad_dispel` | `dispel`, `explosive_dispel` |
| Too many players hit together | Players failed spread | `spread_failure` | `spread`, `chain`, `splash` |
| Too few players hit together | Players failed stack/share | `stack_failure` | `stack`, `shared_damage`, `group_soak` |
| Non-tank got hit by tank/boss attack | Wrong role had threat or positioning | `avoidable_damage` for now, later `tank_hit` or `boss_threat` | `boss_threat`, `tank_buster` |

---

# Fillable Mechanic Form

Copy this section and fill it out before writing the Python block.

```text
MECHANIC DISPLAY NAME:
Example: Void Fall

BOSS / ENCOUNTER:
Example: Imperator Averzian

SPELL ID(S):
Example: 1258883

WHAT TYPE OF EVENT IS THIS IN WARCRAFT LOGS?
[ ] damage_taken
[ ] cast
[ ] aura/debuff
[ ] interrupt
[ ] dispel
[ ] summon
[ ] other: __________

WHAT HAPPENED?
Example: Adds launch a blob into the air. It lands as a void circle. Players hit by the circle take damage.

WHAT DOES FAILURE MEAN?
[ ] Player got hit and should not have
[ ] Enemy cast completed and should have been interrupted
[ ] Too few players soaked
[ ] Player had zero participation
[ ] Player soaked while they should not have
[ ] Debuff was not dispelled
[ ] Debuff was dispelled at the wrong time
[ ] Players failed to spread
[ ] Players failed to stack
[ ] Wrong role/player was hit
[ ] Other: __________

RECOMMENDED failure_type:
Example: avoidable_damage

RECOMMENDED category:
Example: ground_effect

SEVERITY:
[ ] Info
[ ] Warning
[ ] Major
[ ] Critical

WHO CAN FAIL THIS?
[ ] ALL_ROLES
[ ] NON_TANK_ROLES
[ ] TANK_ONLY
[ ] HEALER_ONLY
[ ] DPS_ONLY

IS THIS A PLAYER FAILURE?
[ ] Yes
[ ] No, raid/group failure
[ ] Mixed

MAX REASONABLE HITS:
Example: 1

SCORE PER HIT:
Example: 80

NOTE:
Example: Void circle impact from add projectile.

RECOMMENDATION:
Example: Move out of the landing circle before impact.

SHOULD THIS BE TRACKED?
[ ] Yes
[ ] No, ignore
[ ] Unsure, needs review

WHY SHOULD / SHOULD NOT THIS BE TRACKED?
Example: This is avoidable ground damage and indicates poor movement.
```

---

# Generate Mechanic Block Template

Fill in the placeholders.

```python
MECHANIC_CONSTANT_NAME = {
    "name": "MECHANIC DISPLAY NAME",

    "severity": "Major",
    "avoidable": True,

    "category": "category_here",
    "failure_type": "failure_type_here",

    "counts_as_failure": True,

    "max_reasonable_hits": 1,
    "score_per_hit": 50,

    "applies_to": ALL_ROLES,

    "note": (
        "Briefly explain what the mechanic does."
    ),

    "recommendation": (
        "Tell the player or raid what to do differently."
    ),

    "wcl_type": "damage_taken",
}
```

Then add the spell mapping:

```python
AVOIDABLE_DAMAGE = {
    **mechanic_aliases(
        [SPELL_ID_HERE],
        MECHANIC_CONSTANT_NAME,
    ),
}
```

---

# Example: Avoidable Ground Effect

Use this when the player took damage from something they should have dodged.

```python
VOID_FALL = {
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

Mapping:

```python
**mechanic_aliases(
    [1258883],
    VOID_FALL,
),
```

---

# Example: Traveling Projectile

Use this when players are hit by moving projectiles or missiles.

```python
OBLIVIONS_WRATH = {
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

---

# Example: Missed Interrupt

Use this when an enemy cast completed and should have been stopped.

Important: use the cast spell ID, not the damage spell ID.

```python
SHADOW_FRACTURE = {
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

---

# Example: Minimum Soak

Use this when each soak event requires at least a certain number of players.

Failure is group-level: not enough players soaked.

```python
GLOOM_MINIMUM_SOAK = {
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

---

# Example: Zero Participation

Use this when you want to know who never engaged with a required mechanic.

Example question:

> Did Jimmy never touch Gloom at all?

```python
GLOOM_PARTICIPATION = {
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

# Example: Bad Soak

Use this when taking the soak is bad for certain players.

Example:
- Player has a vulnerability debuff.
- Player already soaked recently.
- Player is the wrong role.
- Player is not assigned to that soak.

```python
BAD_GLOOM_SOAK = {
    "name": "Bad Gloom Soak",

    "severity": "Critical",
    "avoidable": True,

    "category": "bad_soak",
    "failure_type": "bad_soak",

    "counts_as_failure": True,

    "max_reasonable_hits": 0,
    "score_per_hit": 100,

    "applies_to": ALL_ROLES,

    "spell_ids": [1245500],

    "bad_soak_if_aura_ids": [999999],

    "note": (
        "Players with the vulnerability debuff should not soak Gloom."
    ),

    "recommendation": (
        "Do not soak while affected by the vulnerability debuff."
    ),

    "wcl_type": "damage_taken",
}
```

---

# Severity Guide

## Info
Use for low-impact or informational tracking.

Example:
- Minor add damage
- Low-value uptime issue
- Things worth showing but not punishing heavily

## Warning
Use for repeated mistakes or medium-impact mechanics.

Example:
- Projectile hits
- Low participation
- Moderate avoidable damage

## Major
Use for mechanics that strongly affect progression.

Example:
- Missed interrupts
- Major avoidable hit
- Spread failure
- Important dispel failure

## Critical
Use for mechanics that can kill players, wipe the raid, or prevent boss progression.

Example:
- One-shot mechanics
- Required soak failures
- Major tank mechanic failures
- Standing in lethal ground effects

---

# Category Naming Guide

Use lowercase snake_case.

Good examples:

```text
ground_effect
traveling_projectile
frontal
rear_cone
beam
swirl
interrupt
minimum_soak
soak_participation
bad_soak
dispel
spread
stack
boss_threat
tank_buster
add_management
add_priority
movement
bait
```

Avoid:

```text
Ground Effect
Dodge Stuff
Bad
Mechanic
Misc
```

---

# Failure Type Naming Guide

Use these exact values when possible.

```text
avoidable_damage
missed_interrupt
minimum_soak
zero_participation
bad_soak
missed_dispel
bad_dispel
spread_failure
stack_failure
tank_hit
```

If none fit, stop and ask before inventing a new one.

---

# Contributor Checklist

Before submitting a mechanic block:

```text
[ ] Spell ID is confirmed from Warcraft Logs.
[ ] Spell ID is the actual failure event.
[ ] Passive raidwide damage is excluded.
[ ] Player/self-damage spells are excluded.
[ ] The failure_type describes engine behavior.
[ ] The category describes mechanic identity.
[ ] Severity matches progression impact.
[ ] Note explains what happens.
[ ] Recommendation tells players what to do.
[ ] max_reasonable_hits is reasonable.
[ ] score_per_hit is not overly punishing.
[ ] applies_to is correct.
[ ] The mechanic was tested against at least one real report.
```

---

# Common Mistakes

## Mistake: Using category as failure_type

Bad:

```python
"failure_type": "ground_effect"
```

Good:

```python
"category": "ground_effect",
"failure_type": "avoidable_damage",
```

## Mistake: Tracking unavoidable damage

If every player gets hit no matter what, do not track it as a failure.

## Mistake: Tracking the wrong spell ID

Many mechanics have:
- cast ID
- damage ID
- debuff ID
- missile ID
- visual ID

Choose the ID that represents the failure.

## Mistake: Blaming players for group mechanics

Some failures are raid/group failures, not individual failures.

Example:
- minimum_soak
- add lived too long
- missed phase push

Use appropriate failure types and wording.

---

# Community Submission Format

Community contributors can submit this:

```text
Boss:
Spell ID:
Spell Name:
Warcraft Logs event type:
What happened:
Why is this a failure:
Recommended failure_type:
Recommended category:
Severity:
Who can fail:
Suggested note:
Suggested recommendation:
Example Warcraft Logs report:
```

Then a ShortParse maintainer can convert it into the final Python block.
