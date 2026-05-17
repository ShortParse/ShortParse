# ShortParse Mechanic Builder

Use this document to build consistent boss mechanic definitions for ShortParse.

Goal:

1. Identify what happened.
2. Decide what failure means.
3. Choose the correct `failure_type`.
4. Choose a clear `category`.
5. Generate a clean typed Python mechanic block.
6. Add the spell ID mapping with `mechanic_aliases()`.

---

# Typed Mechanic Definitions

ShortParse encounter files should import and use the shared `Mechanic` type:

```python
from shortparse.data.encounters.types import Mechanic
```

Then define mechanics like this:

```python
VOID_FALL: Mechanic = {
    "name": "Void Fall",
    "category": "swirl",
    "failure_type": "avoidable_damage",
}
```

You do not need to change `mechanic_aliases()` or the spell mapping when adding `: Mechanic`.

---

# Quick Decision Matrix

| What happened? | Failure means... | Use `failure_type` | Example `category` |
|---|---|---|---|
| Player got hit by something avoidable | Player took avoidable damage | `avoidable_damage` | `ground_effect`, `traveling_projectile`, `frontal`, `rear_cone`, `swirl`, `beam`, `movement` |
| Enemy cast completed | Cast should have been interrupted | `missed_interrupt` | `interrupt` |
| Too few players soaked | Group failed minimum soak requirement | `minimum_soak` | `minimum_soak`, `group_soak`, `orb_soak` |
| Player never touched/handled mechanic | Player did not participate | `zero_participation` | `soak_participation`, `interrupt_participation`, `add_priority` |
| Player soaked while ineligible | Wrong player soaked | `bad_soak` | `bad_soak`, `vulnerability`, `wrong_assignment` |
| Debuff was not removed in time | Dispel was missed or late | `missed_dispel` | `dispel`, `curse`, `magic`, `poison`, `disease` |
| Debuff was removed at the wrong time | Bad/early/unsafe dispel | `bad_dispel` | `bad_dispel`, `explosive_dispel` |
| Too many players hit together | Players failed spread | `spread_failure` | `spread`, `chain`, `splash` |
| Too few players hit together | Players failed stack/share | `stack_failure` | `stack`, `shared_damage`, `group_soak` |
| Non-tank got hit by tank/boss attack | Wrong role had threat or positioning | `avoidable_damage` for now, later `tank_hit` or `boss_threat` | `boss_threat`, `tank_buster` |
| Player was forced/pulled/knocked into danger | Failed forced movement mechanic | `avoidable_damage` | `forced_movement` |
| Tank was not in boss melee range | Boss positional/tank failure | `boss_range` | `boss_range`, `tank_positioning` |
| Adds lived too long or repeatedly damaged the raid | Raid failed add control | `avoidable_damage` for now, later `add_management` | `add_management`, `add_priority` |
| Dangerous effect triggered after add death | Player failed corpse explosion mechanic | `avoidable_damage` | `corpse_explosion` |
| Player touched a moving lane hazard | Player failed lane movement | `avoidable_damage` | `lane_movement` |
| Player took debuff tick damage | Engine tracks damage ticks, not true dispel timing yet | `avoidable_damage` | `debuff_damage` |

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
[ ] Player was forced/pulled/knocked into danger
[ ] Boss lost valid melee/range target
[ ] Adds lived too long
[ ] Add corpse/post-death effect exploded
[ ] Other: __________

RECOMMENDED failure_type:
Example: avoidable_damage

RECOMMENDED category:
Example: swirl, beam, forced_movement, add_priority

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
Example: Move out of the impact swirl before detonation.

SHOULD THIS BE TRACKED?
[ ] Yes
[ ] No, ignore
[ ] Unsure, needs review

WHY SHOULD / SHOULD NOT THIS BE TRACKED?
Example: This is avoidable damage and indicates poor movement.
```

---

# Generate Mechanic Block Template

```python
MECHANIC_CONSTANT_NAME: Mechanic = {
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

# Example: Swirl

Use this when a telegraphed circle/swirl appears and then detonates.

```python
VOID_FALL: Mechanic = {
    "name": "Void Fall",

    "severity": "Critical",
    "avoidable": True,

    "category": "swirl",
    "failure_type": "avoidable_damage",

    "counts_as_failure": True,

    "max_reasonable_hits": 1,
    "score_per_hit": 80,

    "applies_to": ALL_ROLES,

    "note": (
        "A telegraphed impact swirl appears before detonating."
    ),

    "recommendation": (
        "Move out of the impact swirl before detonation."
    ),

    "wcl_type": "damage_taken",
}
```

---

# Example: Ground Effect

Use this when players stand in lingering bad ground, puddles, pools, or zones.

```python
VOID_ZONE: Mechanic = {
    "name": "Void Zone",

    "severity": "Major",
    "avoidable": True,

    "category": "ground_effect",
    "failure_type": "avoidable_damage",

    "counts_as_failure": True,

    "max_reasonable_hits": 3,
    "score_per_hit": 30,

    "applies_to": ALL_ROLES,

    "note": (
        "Players stood in a lingering ground effect."
    ),

    "recommendation": (
        "Do not stand in lingering ground effects."
    ),

    "wcl_type": "damage_taken",
}
```

---

# Example: Traveling Projectile

Use this when players are hit by moving projectiles or missiles.

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
        "Void projectiles travel outward from the boss, damaging players hit."
    ),

    "recommendation": (
        "Avoid the outward-moving projectiles."
    ),

    "wcl_type": "damage_taken",
}
```

---

# Example: Beam

Use this when players are hit by a beam or laser-style mechanic.

```python
VOID_BREATH: Mechanic = {
    "name": "Void Breath",

    "severity": "Critical",
    "avoidable": True,

    "category": "beam",
    "failure_type": "avoidable_damage",

    "counts_as_failure": True,

    "max_reasonable_hits": 0,
    "score_per_hit": 100,

    "applies_to": ALL_ROLES,

    "note": (
        "The boss sweeps a deadly beam across the room."
    ),

    "recommendation": (
        "Avoid touching the beam."
    ),

    "wcl_type": "damage_taken",
}
```

---

# Example: Missed Interrupt

Use this when an enemy cast completed and should have been stopped.

Important: use the cast spell ID, not the damage spell ID.

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

---

# Example: Minimum Soak

Use this when each soak event requires at least a certain number of players.

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
        "Assign soak groups and make sure enough eligible players soak."
    ),

    "wcl_type": "damage_taken",
}
```

---

# Example: Zero Participation

Use this when you want to know who never engaged with a required mechanic.

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

# Example: Bad Soak

Use this when taking the soak is bad for certain players.

```python
BAD_GLOOM_SOAK: Mechanic = {
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

# Example: Forced Movement

Use this when a player is pulled, pushed, knocked back, or otherwise forced into danger.

```python
FALLING: Mechanic = {
    "name": "Falling",

    "severity": "Critical",
    "avoidable": True,

    "category": "forced_movement",
    "failure_type": "avoidable_damage",

    "counts_as_failure": True,

    "max_reasonable_hits": 0,
    "score_per_hit": 100,

    "applies_to": ALL_ROLES,

    "note": (
        "Players were knocked, pulled, or forced into lethal space."
    ),

    "recommendation": (
        "Position carefully to avoid being forced into danger."
    ),

    "wcl_type": "damage_taken",
}
```

---

# Example: Boss Range

Use this when the boss should always have a valid tank/melee target nearby.

```python
OVERPOWERING_PULSE: Mechanic = {
    "name": "Overpowering Pulse",

    "severity": "Critical",
    "avoidable": True,

    "category": "boss_range",
    "failure_type": "boss_range",

    "counts_as_failure": True,

    "max_reasonable_hits": 0,
    "score_per_hit": 100,

    "applies_to": TANK_ONLY,

    "note": (
        "The boss emitted a pulse because no valid tank remained in range."
    ),

    "recommendation": (
        "Keep a tank in proper boss range at all times."
    ),

    "wcl_type": "damage_taken",
}
```

---

# Example: Corpse Explosion

Use this when an add leaves behind a dangerous explosion or puddle after death.

```python
DARK_GOO: Mechanic = {
    "name": "Dark Goo",

    "severity": "Warning",
    "avoidable": True,

    "category": "corpse_explosion",
    "failure_type": "avoidable_damage",

    "counts_as_failure": True,

    "max_reasonable_hits": 4,
    "score_per_hit": 20,

    "applies_to": ALL_ROLES,

    "note": (
        "The add exploded after death, leaving dangerous ground effects."
    ),

    "recommendation": (
        "Move away from add corpses before they explode."
    ),

    "wcl_type": "damage_taken",
}
```

---

# Example: Add Management

Use this when adds lived too long or repeatedly damaged the raid.

```python
BLISTERBURST: Mechanic = {
    "name": "Blisterburst",

    "severity": "Warning",
    "avoidable": True,

    "category": "add_management",
    "failure_type": "avoidable_damage",

    "counts_as_failure": True,

    "max_reasonable_hits": 10,
    "score_per_hit": 10,

    "applies_to": ALL_ROLES,

    "note": (
        "Adds survived too long and repeatedly damaged the raid."
    ),

    "recommendation": (
        "Prioritize killing or controlling the adds faster."
    ),

    "wcl_type": "damage_taken",
}
```

---

# Example: Add Priority

Use this when specific priority adds or orbs must be killed before they empower the boss or trigger raid damage.

```python
VOID_INFUSION: Mechanic = {
    "name": "Void Infusion",

    "severity": "Critical",
    "avoidable": True,

    "category": "add_priority",
    "failure_type": "avoidable_damage",

    "counts_as_failure": True,

    "max_reasonable_hits": 0,
    "score_per_hit": 100,

    "applies_to": ALL_ROLES,

    "note": (
        "Priority orbs were not killed before the boss absorbed them."
    ),

    "recommendation": (
        "Prioritize killing the orbs before the boss reaches them."
    ),

    "wcl_type": "damage_taken",
}
```

---

# Example: Lane Movement

Use this when players must avoid marching adds, moving lanes, or lane-based hazards.

```python
SHADOW_PHALANX: Mechanic = {
    "name": "Shadow Phalanx",

    "severity": "Critical",
    "avoidable": True,

    "category": "lane_movement",
    "failure_type": "avoidable_damage",

    "counts_as_failure": True,

    "max_reasonable_hits": 0,
    "score_per_hit": 100,

    "applies_to": ALL_ROLES,

    "note": (
        "The boss sends units marching through a lane."
    ),

    "recommendation": (
        "Avoid touching the marching lane hazard."
    ),

    "wcl_type": "damage_taken",
}
```

---

# Example: Debuff Damage

Use this when the current engine is only tracking damage ticks from a debuff.

```python
BLACK_MIASMA: Mechanic = {
    "name": "Black Miasma",

    "severity": "Warning",
    "avoidable": False,

    "category": "debuff_damage",
    "failure_type": "avoidable_damage",

    "counts_as_failure": True,

    "max_reasonable_hits": 4,
    "score_per_hit": 20,

    "applies_to": ALL_ROLES,

    "note": (
        "Players are afflicted with a debuff that causes ticking damage."
    ),

    "recommendation": (
        "Remove the debuff quickly when possible."
    ),

    "wcl_type": "damage_taken",
}
```

Use `missed_dispel` later when the engine is tracking aura duration, dispel timing, or actual dispel events.

---

# Severity Guide

## Info

Use for low-impact or informational tracking.

Examples:
- Minor add damage
- Low-value uptime issue
- Things worth showing but not punishing heavily

## Warning

Use for repeated mistakes or medium-impact mechanics.

Examples:
- Projectile hits
- Low participation
- Moderate avoidable damage

## Major

Use for mechanics that strongly affect progression.

Examples:
- Missed interrupts
- Major avoidable hit
- Spread failure
- Important dispel failure

## Critical

Use for mechanics that can kill players, wipe the raid, or prevent boss progression.

Examples:
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
movement
forced_movement
interrupt
minimum_soak
soak_participation
bad_soak
dispel
spread
stack
boss_threat
boss_range
tank_buster
tank_positioning
add_management
add_priority
corpse_explosion
lane_movement
debuff_damage
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
boss_range
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
