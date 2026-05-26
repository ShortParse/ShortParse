# ShortParse Encounter Database Audit Report

This report provides an automated audit of the encounter database definitions across all raids and boss fights. It is designed to flag 'unfair' mechanics (unavoidable damage marked as failures), severity-score mismatches, missing details, and duplicate mappings.

## Summary

* **Total unique mechanics audited:** 100
* **Total anomalies/issues detected:** 31

### Issues Breakdown by Severity

| Severity | Count | Action Required |
|---|---|---|
| 🔴 **Critical** | 0 | Imports failed, database cannot load. Fix immediately! |
| 🟠 **High** | 0 | Unfair mechanics or duplicate mappings. High risk of false dings. |
| 🟡 **Medium** | 31 | Severity and score mismatches. Inconsistent scoring weights. |
| 🔵 **Low** | 0 | Missing descriptive notes or recommendations. |

## Detected Issues

### 1. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `the_voidspire`
* **Boss:** `Crown of the Cosmos`
* **Mechanic:** `Grasp of Emptiness`

> **Audit Finding:** Severity is 'Major' but score_per_hit is 40. Expected 50 to 79.

---

### 2. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `the_voidspire`
* **Boss:** `Crown of the Cosmos`
* **Mechanic:** `Void Expulsion`

> **Audit Finding:** Severity is 'Major' but score_per_hit is 35. Expected 50 to 79.

---

### 3. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `the_voidspire`
* **Boss:** `Crown of the Cosmos`
* **Mechanic:** `Void Remnants`

> **Audit Finding:** Severity is 'Major' but score_per_hit is 25. Expected 50 to 79.

---

### 4. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `the_voidspire`
* **Boss:** `Crown of the Cosmos`
* **Mechanic:** `Ravenous Abyss`

> **Audit Finding:** Severity is 'Major' but score_per_hit is 30. Expected 50 to 79.

---

### 5. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `the_voidspire`
* **Boss:** `Crown of the Cosmos`
* **Mechanic:** `Silverstrike Barrage`

> **Audit Finding:** Severity is 'Major' but score_per_hit is 35. Expected 50 to 79.

---

### 6. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `the_voidspire`
* **Boss:** `Crown of the Cosmos`
* **Mechanic:** `Orbiting Matter`

> **Audit Finding:** Severity is 'Major' but score_per_hit is 40. Expected 50 to 79.

---

### 7. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `the_voidspire`
* **Boss:** `Crown of the Cosmos`
* **Mechanic:** `Singularity Eruption`

> **Audit Finding:** Severity is 'Major' but score_per_hit is 35. Expected 50 to 79.

---

### 8. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `the_voidspire`
* **Boss:** `Crown of the Cosmos`
* **Mechanic:** `Dark Hand`

> **Audit Finding:** Severity is 'Critical' but score_per_hit is only 60. Expected >= 70.

---

### 9. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `the_voidspire`
* **Boss:** `Crown of the Cosmos`
* **Mechanic:** `Rift Slash`

> **Audit Finding:** Severity is 'Major' but score_per_hit is 30. Expected 50 to 79.

---

### 10. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `the_voidspire`
* **Boss:** `Fallen-King Salhadaar`
* **Mechanic:** `Shadow Fracture`

> **Audit Finding:** Severity is 'Major' but score_per_hit is 80. Expected 50 to 79.

---

### 11. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `the_voidspire`
* **Boss:** `Fallen-King Salhadaar`
* **Mechanic:** `Twilight Spikes`

> **Audit Finding:** Severity is 'Major' but score_per_hit is 30. Expected 50 to 79.

---

### 12. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `the_voidspire`
* **Boss:** `Fallen-King Salhadaar`
* **Mechanic:** `Void Crush`

> **Audit Finding:** Severity is 'Info' but score_per_hit is 20. Expected 0 to 19.

---

### 13. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `the_voidspire`
* **Boss:** `Fallen-King Salhadaar`
* **Mechanic:** `Quintessence`

> **Audit Finding:** Severity is 'Major' but score_per_hit is 20. Expected 50 to 79.

---

### 14. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `the_voidspire`
* **Boss:** `Lightblinded Vanguard`
* **Mechanic:** `Divine Hammer`

> **Audit Finding:** Severity is 'Major' but score_per_hit is 40. Expected 50 to 79.

---

### 15. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `the_voidspire`
* **Boss:** `Lightblinded Vanguard`
* **Mechanic:** `Divine Toll`

> **Audit Finding:** Severity is 'Major' but score_per_hit is 45. Expected 50 to 79.

---

### 16. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `the_voidspire`
* **Boss:** `Lightblinded Vanguard`
* **Mechanic:** `Judgment`

> **Audit Finding:** Severity is 'Critical' but score_per_hit is only 50. Expected >= 70.

---

### 17. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `the_voidspire`
* **Boss:** `Lightblinded Vanguard`
* **Mechanic:** `Final Verdict`

> **Audit Finding:** Severity is 'Critical' but score_per_hit is only 60. Expected >= 70.

---

### 18. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `the_voidspire`
* **Boss:** `Lightblinded Vanguard`
* **Mechanic:** `Shield of the Righteous`

> **Audit Finding:** Severity is 'Critical' but score_per_hit is only 60. Expected >= 70.

---

### 19. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `the_voidspire`
* **Boss:** `Lightblinded Vanguard`
* **Mechanic:** `Exorcism`

> **Audit Finding:** Severity is 'Major' but score_per_hit is 30. Expected 50 to 79.

---

### 20. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `the_voidspire`
* **Boss:** `Vaelgor & Ezzorak`
* **Mechanic:** `Vaelwing`

> **Audit Finding:** Severity is 'Major' but score_per_hit is 100. Expected 50 to 79.

---

### 21. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `the_voidspire`
* **Boss:** `Vaelgor & Ezzorak`
* **Mechanic:** `Rakfang`

> **Audit Finding:** Severity is 'Major' but score_per_hit is 100. Expected 50 to 79.

---

### 22. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `the_voidspire`
* **Boss:** `Vorasius`
* **Mechanic:** `Aftershock`

> **Audit Finding:** Severity is 'Critical' but score_per_hit is only 60. Expected >= 70.

---

### 23. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `the_voidspire`
* **Boss:** `Vorasius`
* **Mechanic:** `Blisterburst`

> **Audit Finding:** Severity is 'Warning' but score_per_hit is 10. Expected 20 to 49.

---

### 24. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `the_dreamrift`
* **Boss:** `Chimaerus the Undreamt God`
* **Mechanic:** `Dissonance`

> **Audit Finding:** Severity is 'Major' but score_per_hit is 40. Expected 50 to 79.

---

### 25. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `the_dreamrift`
* **Boss:** `Chimaerus the Undreamt God`
* **Mechanic:** `Essence Bolt`

> **Audit Finding:** Severity is 'Info' but score_per_hit is 20. Expected 0 to 19.

---

### 26. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `march_on_queldanas`
* **Boss:** `Belo'ren, Child of Al'ar`
* **Mechanic:** `Death Drop`

> **Audit Finding:** Severity is 'Major' but score_per_hit is 40. Expected 50 to 79.

---

### 27. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `march_on_queldanas`
* **Boss:** `Midnight Falls`
* **Mechanic:** `Death's Dirge`

> **Audit Finding:** Severity is 'Major' but score_per_hit is 40. Expected 50 to 79.

---

### 28. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `march_on_queldanas`
* **Boss:** `Midnight Falls`
* **Mechanic:** `Cosmic Fission`

> **Audit Finding:** Severity is 'Major' but score_per_hit is 40. Expected 50 to 79.

---

### 29. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `march_on_queldanas`
* **Boss:** `Midnight Falls`
* **Mechanic:** `Heaven's Glaives`

> **Audit Finding:** Severity is 'Major' but score_per_hit is 35. Expected 50 to 79.

---

### 30. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `march_on_queldanas`
* **Boss:** `Midnight Falls`
* **Mechanic:** `Dark Constellation`

> **Audit Finding:** Severity is 'Major' but score_per_hit is 40. Expected 50 to 79.

---

### 31. 🟡 Severity-Score Mismatch (Medium Severity)
* **Raid:** `march_on_queldanas`
* **Boss:** `Midnight Falls`
* **Mechanic:** `Midnight`

> **Audit Finding:** Severity is 'Critical' but score_per_hit is only 60. Expected >= 70.

---

