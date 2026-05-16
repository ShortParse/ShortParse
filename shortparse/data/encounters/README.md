# ShortParse Encounter Database

This folder contains the encounter intelligence system used by ShortParse.

Each boss encounter contains manually curated avoidable mechanics, role filtering rules, severity classifications, and coaching recommendations used throughout the platform.

---

# Additional Documentation

- `README/mechanic_builder.md`
- `README/mechanic_decision_matrix.md`

---

# Folder Structure

```text
encounters/
├── README.md
├── constants.py
├── mechanic_helper.py
├── registry.py
│
├── march_on_queldanas/
│   ├── __init__.py
│   ├── beloren_child_of_alar.py
│   └── midnight_falls.py
│
├── the_voidspire/
│   ├── __init__.py
│   ├── imperator_averzian.py
│   ├── vorasius.py
│   ├── fallen_king_salhadaar.py
│   ├── vaelgor_ezzorak.py
│   ├── lightblinded_vanguard.py
│   └── crown_of_the_cosmos.py
│
└── the_dreamrift/
    ├── __init__.py
    └── chimaerus.py
```

---

# Role Constants

Import these at the top of every boss encounter file:

```python
from shortparse.data.encounters.constants import (
    ALL_ROLES,
    NON_TANK_ROLES,
    DPS_ONLY,
    HEALER_ONLY,
    TANK_ONLY,
)
```

## ALL_ROLES

Use when ANY player hit by the mechanic should be counted.

Examples:

* avoidable swirlies
* avoidable puddles
* avoidable explosions
* avoidable movement mechanics

```python
"applies_to": ALL_ROLES
```

---

## NON_TANK_ROLES

Use when tanks are EXPECTED to take the mechanic, but DPS/healers should NOT be hit.

Examples:

* tank soak
* tank frontal
* tank cleave

```python
"applies_to": NON_TANK_ROLES
```

---

## DPS_ONLY

Use when only DPS players should be evaluated.

Rare.

```python
"applies_to": DPS_ONLY
```

---

## HEALER_ONLY

Use when only healers should be evaluated.

Rare.

```python
"applies_to": HEALER_ONLY
```

---

## TANK_ONLY

Use when only tanks should be evaluated.

Examples:

* tank defensive failure
* failed taunt swap
* tank-only mechanic failure

```python
"applies_to": TANK_ONLY
```

---

# Boss File Structure

Each boss file should export:

```python
ENCOUNTER_ID = 3183
ENCOUNTER_NAME = "Midnight Falls"

AVOIDABLE_DAMAGE = {
    ...
}
```

---

# Mechanic Helpers

Some mechanics use MULTIPLE Warcraft Logs spell IDs while still representing the SAME mechanic.

To avoid duplicating mechanic data, ShortParse uses helper functions.

Import:

```python
from shortparse.data.encounters.mechanic_helper import (
    mechanic_aliases,
)
```

---

## Example

```python
VOID_RUPTURE = {
    "name": "Void Rupture",
    "severity": "Critical",
    "avoidable": True,
    "category": "Ground Effect",
    "failure_type": "Repeated avoidable hits",
    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 80,
    "applies_to": ALL_ROLES,
    "note": (
        "The remaining add will explode in a 12yd range "
        "and several beams will shoot out from the "
        "claimed space for a short time."
    ),
    "recommendation": (
        "Review movement pathing and avoid blue circles "
        "on the floor."
    ),
    "wcl_type": "damage_taken",
}

AVOIDABLE_DAMAGE = {

    # Void Rupture
    **mechanic_aliases(
        [1261249, 1279890],
        VOID_RUPTURE,
    ),

}
```

This automatically creates one mechanic entry per spell ID while keeping the mechanic definition centralized.

Benefits:

* cleaner files
* less duplication
* easier maintenance
* automatic spell_id assignment
* easier future raid additions

---

# Mechanic Structure

```python
1254076: {
    "name": "Heaven's Glaives",
    "severity": "Critical",

    "avoidable": True,
    "category": "Movement",
    "failure_type": "Repeated avoidable hits",

    "counts_as_failure": True,
    "max_reasonable_hits": 1,
    "score_per_hit": 20,

    "applies_to": ALL_ROLES,

    "note": (
        "Avoidable blade hits. Repeated hits usually "
        "indicate poor movement or bad positioning."
    ),

    "recommendation": (
        "Review movement pathing and avoid standing "
        "in blade travel lines."
    ),

    "wcl_type": "damage_taken",
},
```

---

# Field Explanations

## `name`

Human-readable mechanic name shown on the website/UI.

---

## `severity`

Allowed values:

```python
"Critical"
"Major"
"Warning"
"Info"
```

---

## `avoidable`

```python
True
```

Players should avoid this mechanic.

```python
False
```

Intended/unavoidable damage.

---

## `category`

Suggested categories:

```python
"Movement"
"Ground Effect"
"Spread"
"Stack"
"Soak"
"Interrupt"
"Defensive"
"Tank"
"Frontal"
"Debuff"
"Raid Damage"
```

---

## `failure_type`

Short explanation describing WHY the mechanic matters.

Examples:

```python
"Repeated avoidable hits"
"Failed soak"
"Missed interrupt"
"Improper defensive usage"
"Non-tank hit by tank mechanic"
```

---

## `counts_as_failure`

Controls whether the mechanic contributes to issue scoring.

---

## `max_reasonable_hits`

Maximum acceptable hits before penalties become severe.

Examples:

```python
0 = Never acceptable
1 = One accidental hit may be tolerated
3 = Repeated hits somewhat expected
```

---

## `score_per_hit`

Suggested scoring ranges:

```python
10-25  = light warning
30-60  = serious mechanic failure
80-100 = severe / potentially wipe-causing failure
```

---

## `applies_to`

Controls which player roles should be evaluated.

If a player's role is NOT listed here, the hit is ignored.

Examples:

```python
"applies_to": ALL_ROLES
"applies_to": NON_TANK_ROLES
"applies_to": TANK_ONLY
```

---

## `note`

Short explanation shown on the website.

---

## `recommendation`

Coaching guidance or suggested improvement.

---

## `wcl_type`

Usually:

```python
"damage_taken"
"buff_applied"
"debuff_applied"
"cast_success"
"death"
"interrupt"
"dispel"
```

---

# Warcraft Logs Source

Spell IDs are typically found under:

```text
Analyze Report
→ Damage Taken
→ All Abilities
```

or:

```text
Analyze Report
→ Events
→ Ability
```

---

# Philosophy

ShortParse prioritizes:

* actionable coaching
* role-aware analysis
* avoidable failure detection
* progression-focused feedback
* realistic raid evaluation

The encounter database is intended to evolve over time as new encounters, edge cases, and role interactions are discovered.
