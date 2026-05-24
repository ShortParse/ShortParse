# shortparse/data/cooldowns/__init__.py

import os
import importlib

RAID_COOLDOWNS = {}

# Discover and load all class-specific cooldowns
current_dir = os.path.dirname(__file__)
for item in os.listdir(current_dir):
    item_path = os.path.join(current_dir, item)
    if os.path.isdir(item_path) and not item.startswith("__"):
        for filename in os.listdir(item_path):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                full_module_name = f"shortparse.data.cooldowns.{item}.{module_name}"
                try:
                    mod = importlib.import_module(full_module_name)
                    cooldowns_dict = getattr(mod, "COOLDOWNS", None)
                    if isinstance(cooldowns_dict, dict):
                        RAID_COOLDOWNS.update(cooldowns_dict)
                except Exception:
                    pass

RAID_COOLDOWN_IDS = set(RAID_COOLDOWNS.keys())


def get_cooldown(spell_id: int) -> dict | None:
    return RAID_COOLDOWNS.get(spell_id)


def is_raid_cooldown(spell_id: int) -> bool:
    return spell_id in RAID_COOLDOWN_IDS


def normalize_class_name(class_name: str) -> str:
    return (
        str(class_name or "")
        .replace(" ", "")
        .replace("_", "")
        .upper()
    )


def get_cooldowns_for_class(
    class_name: str,
    spec_name: str | None = None,
) -> dict:
    normalized_class = normalize_class_name(class_name)
    normalized_spec = normalize_class_name(spec_name or "")

    results = {}

    for spell_id, cooldown in RAID_COOLDOWNS.items():
        cooldown_class = normalize_class_name(
            cooldown.get("class")
        )

        if cooldown_class != normalized_class:
            continue

        cooldown_specs = cooldown.get("specs")

        if cooldown_specs:
            normalized_specs = {
                normalize_class_name(spec)
                for spec in cooldown_specs
            }

            if normalized_spec not in normalized_specs:
                continue

        results[spell_id] = cooldown

    return results
