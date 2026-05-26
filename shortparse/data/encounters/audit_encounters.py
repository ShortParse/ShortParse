#!/usr/bin/env python3
import os
import sys

# Remove the script's directory from sys.path to prevent naming collisions with stdlib types.py
script_dir = os.path.abspath(os.path.dirname(__file__))
sys.path = [p for p in sys.path if os.path.abspath(p) != script_dir]

# Ensure shortparse package is importable by appending workspace root
sys.path.insert(0, os.path.abspath(os.path.join(script_dir, "../../../")))

import importlib
import typing

def main():
    print("======================================================================")
    print("ShortParse Encounter Database Audit Tool")
    print("======================================================================")
    
    # Locate encounters directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    raids = ["the_voidspire", "the_dreamrift", "march_on_queldanas"]
    
    issues_found = []
    total_mechanics = 0
    all_spell_ids = {}
    
    print("\n[+] Gathering and parsing boss encounter configuration files...")
    
    for raid in raids:
        raid_dir = os.path.join(base_dir, raid)
        if not os.path.isdir(raid_dir):
            continue
            
        print(f"\n  Raid: {raid}")
        
        # Walk files
        for filename in sorted(os.listdir(raid_dir)):
            if not filename.endswith(".py") or filename == "__init__.py":
                continue
                
            module_name = filename[:-3]
            full_module_path = f"shortparse.data.encounters.{raid}.{module_name}"
            
            try:
                # Dynamic import
                module = importlib.import_module(full_module_path)
                encounter_name = getattr(module, "ENCOUNTER_NAME", module_name.replace("_", " ").title())
                encounter_id = getattr(module, "ENCOUNTER_ID", "Unknown")
                avoidable_damage = getattr(module, "AVOIDABLE_DAMAGE", {})
                
                print(f"    - {encounter_name} (ID: {encounter_id}) - {len(avoidable_damage)} spell mappings")
                
                # We want to collect all unique mechanics defined in this boss
                # Since AVOIDABLE_DAMAGE maps spell ID -> Mechanic dict, several spell IDs might map to the same Mechanic object
                # Let's group them by mechanic name to analyze each mechanic once per boss!
                mechanic_groups = {}
                for spell_id, mechanic in avoidable_damage.items():
                    mech_name = mechanic.get("name", "Unnamed Mechanic")
                    if mech_name not in mechanic_groups:
                        mechanic_groups[mech_name] = {
                            "mechanic": mechanic,
                            "spell_ids": []
                        }
                    mechanic_groups[mech_name]["spell_ids"].append(spell_id)
                    
                    # Track global spell IDs to find duplicates
                    if spell_id in all_spell_ids:
                        all_spell_ids[spell_id].append((encounter_name, mech_name))
                    else:
                        all_spell_ids[spell_id] = [(encounter_name, mech_name)]
                
                for mech_name, group in mechanic_groups.items():
                    total_mechanics += 1
                    mech = group["mechanic"]
                    spells = group["spell_ids"]
                    
                    # Perform Audits:
                    
                    # 1. Unfairness Check: Unavoidable but counts as failure
                    avoidable = mech.get("avoidable", True)
                    counts_as_failure = mech.get("counts_as_failure", True)
                    severity = mech.get("severity", "Warning")
                    score = mech.get("score_per_hit", 0)
                    
                    if not avoidable and counts_as_failure:
                        issues_found.append({
                            "raid": raid,
                            "boss": encounter_name,
                            "mechanic": mech_name,
                            "type": "Unfair Mechanic",
                            "severity": "High",
                            "description": f"Mechanic is marked as 'avoidable: False' but 'counts_as_failure: True' with score penalty {score}. This unfairly penalizes players for unavoidable raid damage."
                        })
                        
                    # 2. Score vs Severity Consistency Checks
                    if severity == "Critical" and score < 70:
                        issues_found.append({
                            "raid": raid,
                            "boss": encounter_name,
                            "mechanic": mech_name,
                            "type": "Severity-Score Mismatch",
                            "severity": "Medium",
                            "description": f"Severity is 'Critical' but score_per_hit is only {score}. Expected >= 70."
                        })
                    elif severity == "Major" and (score < 50 or score >= 80):
                        issues_found.append({
                            "raid": raid,
                            "boss": encounter_name,
                            "mechanic": mech_name,
                            "type": "Severity-Score Mismatch",
                            "severity": "Medium",
                            "description": f"Severity is 'Major' but score_per_hit is {score}. Expected 50 to 79."
                        })
                    elif severity == "Warning" and (score < 20 or score >= 50):
                        issues_found.append({
                            "raid": raid,
                            "boss": encounter_name,
                            "mechanic": mech_name,
                            "type": "Severity-Score Mismatch",
                            "severity": "Medium",
                            "description": f"Severity is 'Warning' but score_per_hit is {score}. Expected 20 to 49."
                        })
                    elif severity == "Info" and score >= 20:
                        issues_found.append({
                            "raid": raid,
                            "boss": encounter_name,
                            "mechanic": mech_name,
                            "type": "Severity-Score Mismatch",
                            "severity": "Medium",
                            "description": f"Severity is 'Info' but score_per_hit is {score}. Expected 0 to 19."
                        })
                        
                    # 3. Missing Fields
                    if not mech.get("note"):
                        issues_found.append({
                            "raid": raid,
                            "boss": encounter_name,
                            "mechanic": mech_name,
                            "type": "Missing Documentation",
                            "severity": "Low",
                            "description": "Mechanic is missing a descriptive 'note' field."
                        })
                    if not mech.get("recommendation"):
                        issues_found.append({
                            "raid": raid,
                            "boss": encounter_name,
                            "mechanic": mech_name,
                            "type": "Missing Documentation",
                            "severity": "Low",
                            "description": "Mechanic is missing a 'recommendation' field."
                        })
                        
            except Exception as e:
                print(f"    - [ERROR] Failed to load {module_name}: {e}")
                issues_found.append({
                    "raid": raid,
                    "boss": module_name,
                    "mechanic": "None",
                    "type": "Import Failure",
                    "severity": "Critical",
                    "description": f"Module failed to import: {e}"
                })
                
    # 4. Check Duplicate Spell IDs
    for spell_id, occurrences in all_spell_ids.items():
        if len(occurrences) > 1:
            boss_list = ", ".join([f"{occ[0]} ({occ[1]})" for occ in occurrences])
            issues_found.append({
                "raid": "Global",
                "boss": "Multiple",
                "mechanic": f"Spell ID {spell_id}",
                "type": "Duplicate Spell ID Mappings",
                "severity": "High",
                "description": f"Spell ID {spell_id} is registered in multiple mechanics: {boss_list}."
            })
            
    print("\n======================================================================")
    print("Audit Results")
    print("======================================================================")
    print(f"Total Mechanics Audited: {total_mechanics}")
    print(f"Total Issues Detected: {len(issues_found)}")
    
    # Sort issues by severity: Critical, High, Medium, Low
    sev_map = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
    issues_found.sort(key=lambda x: sev_map.get(x["severity"], 0), reverse=True)
    
    for i, issue in enumerate(issues_found, 1):
        print(f"\n{i}. [{issue['severity']} Severity] - {issue['type']}")
        print(f"   Location: {issue['raid']} -> {issue['boss']} -> {issue['mechanic']}")
        print(f"   Description: {issue['description']}")
        
    # Write a beautiful markdown report
    report_path = os.path.join(base_dir, "encounter_audit_report.md")
    write_markdown_report(report_path, total_mechanics, issues_found)
    print(f"\n[+] A detailed markdown audit report has been written to: {report_path}")

def write_markdown_report(report_path, total_mechanics, issues):
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# ShortParse Encounter Database Audit Report\n\n")
        f.write("This report provides an automated audit of the encounter database definitions across all raids and boss fights. It is designed to flag 'unfair' mechanics (unavoidable damage marked as failures), severity-score mismatches, missing details, and duplicate mappings.\n\n")
        
        f.write("## Summary\n\n")
        f.write(f"* **Total unique mechanics audited:** {total_mechanics}\n")
        f.write(f"* **Total anomalies/issues detected:** {len(issues)}\n\n")
        
        if len(issues) == 0:
            f.write("### ✨ Perfect Database Health!\n")
            f.write("No issues or mismatches were found. All mechanics are fair, correctly weighted, and fully documented!\n")
            return
            
        # Count by severity
        crit = sum(1 for x in issues if x["severity"] == "Critical")
        high = sum(1 for x in issues if x["severity"] == "High")
        med = sum(1 for x in issues if x["severity"] == "Medium")
        low = sum(1 for x in issues if x["severity"] == "Low")
        
        f.write("### Issues Breakdown by Severity\n\n")
        f.write(f"| Severity | Count | Action Required |\n")
        f.write(f"|---|---|---|\n")
        f.write(f"| 🔴 **Critical** | {crit} | Imports failed, database cannot load. Fix immediately! |\n")
        f.write(f"| 🟠 **High** | {high} | Unfair mechanics or duplicate mappings. High risk of false dings. |\n")
        f.write(f"| 🟡 **Medium** | {med} | Severity and score mismatches. Inconsistent scoring weights. |\n")
        f.write(f"| 🔵 **Low** | {low} | Missing descriptive notes or recommendations. |\n\n")
        
        f.write("## Detected Issues\n\n")
        
        for i, issue in enumerate(issues, 1):
            sev_icon = "🔴" if issue["severity"] == "Critical" else "🟠"
            if issue["severity"] == "High": sev_icon = "🟠"
            elif issue["severity"] == "Medium": sev_icon = "🟡"
            elif issue["severity"] == "Low": sev_icon = "🔵"
            
            f.write(f"### {i}. {sev_icon} {issue['type']} ({issue['severity']} Severity)\n")
            f.write(f"* **Raid:** `{issue['raid']}`\n")
            f.write(f"* **Boss:** `{issue['boss']}`\n")
            f.write(f"* **Mechanic:** `{issue['mechanic']}`\n\n")
            f.write(f"> **Audit Finding:** {issue['description']}\n\n")
            f.write("---\n\n")

if __name__ == "__main__":
    main()
