import importlib
import sys
from pathlib import Path
from shortparse.logging import get_logger

logger = get_logger(__name__)

# Dynamic module discovery to avoid manual hardcoding of new raids
ENCOUNTER_MODULES = []

def load_encounter_modules():
    global ENCOUNTER_MODULES
    modules = []
    
    base_dir = Path(__file__).resolve().parent
    for item in base_dir.iterdir():
        if item.is_dir() and not item.name.startswith("__") and not item.name.startswith("."):
            init_file = item / "__init__.py"
            if init_file.exists():
                module_name = f"shortparse.data.encounters.{item.name}"
                try:
                    if module_name in sys.modules:
                        mod = importlib.reload(sys.modules[module_name])
                    else:
                        mod = importlib.import_module(module_name)
                    
                    if hasattr(mod, "AVOIDABLE_DAMAGE_BY_ENCOUNTER_ID"):
                        modules.append(mod)
                except Exception as e:
                    logger.error(f"Failed to dynamically load encounter module {module_name}: {e}")
    ENCOUNTER_MODULES = modules

# Initial load
load_encounter_modules()

def get_avoidable_damage(encounter_id: int) -> dict:
    # Ensure fresh loads in case new modules were compiled dynamically during runtime
    load_encounter_modules()
    
    for module in ENCOUNTER_MODULES:
        mechanics = getattr(module, "AVOIDABLE_DAMAGE_BY_ENCOUNTER_ID", {}).get(encounter_id)
        if mechanics:
            return mechanics

    return {}