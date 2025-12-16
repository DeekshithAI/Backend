# backend/sideview/aggregator.py

CRITICAL = {"bud_rot", "bud_root_dropping", "stem_bleeding"}

MIN_CONF = 0.35
MIN_SAMPLES = 2


def normalize_status(s):
    # Normalize status strings to a consistent token format
    # - strip whitespace
    # - lowercase
    # - convert spaces to underscores so names like 'bud rot' -> 'bud_rot'
    return s.strip().lower().replace(" ", "_")


def part_summary(items):
    """
    Summaries each part (stem, bud, leaves) based on multiple frame predictions.
    """

    # Filter out low-confidence predictions
    items = [
        {
            "status": normalize_status(i["status"]),
            "confidence": float(i.get("confidence", 1.0))
        }
        for i in items
        if float(i.get("confidence", 1.0)) >= MIN_CONF
    ]

    n = len(items)
    if n == 0:
        return {
            "health_percentage": None,
            "status": "no_data",
            "samples": 0,
            "top_disease": None
        }

    # Weighted health percentage
    total_w = sum(i["confidence"] for i in items)
    
    # Count critical and healthy items
    critical_w = sum(i["confidence"] for i in items if i["status"] in CRITICAL or i["status"] == "critical")
    healthy_w = sum(i["confidence"] for i in items if i["status"] == "healthy")

    # If critical disease detected, return as critical
    if critical_w > 0:
        health_pct = 0.0  # Critical = 0% health
        status = "critical"
    else:
        health_pct = round((healthy_w / total_w) * 100, 2) if total_w else None
        status = "healthy" if health_pct and health_pct >= 50 else "not healthy"

    from collections import defaultdict
    counts = defaultdict(float)
    confs = defaultdict(list)

    for it in items:
        counts[it["status"]] += 1
        confs[it["status"]].append(it["confidence"])

    top = max(counts.items(), key=lambda x: (x[1], sum(confs[x[0]])/len(confs[x[0]])))[0]
    top_conf = round(sum(confs[top]) / len(confs[top]), 3)

    return {
        "health_percentage": health_pct,
        "status": status,
        "samples": n,
        "top_disease": (top, top_conf)
    }


def aggregate_health_robust(data):
    """
    Final decision for entire tree, applying critical disease override.
    """

    parts = {}
    critical_flag = False
    critical_reason = None
    valid_parts = []

    for part in ["stem", "bud", "leaves"]:
        summary = part_summary(data.get(part, []))
        parts[part] = summary

        # Check for critical diseases or critical status
        if summary["top_disease"]:
            disease_name = summary["top_disease"][0]
            if disease_name in CRITICAL or disease_name == "critical" or summary["status"] == "critical":
                critical_flag = True
                critical_reason = disease_name

        if summary["health_percentage"] is not None:
            valid_parts.append(summary["health_percentage"])

    # If NO useful data
    if not valid_parts:
        if critical_flag:
            # Critical disease found - very low health
            final_health = 0.0
            final_status = "unhealthy"
        else:
            final_health = None
            final_status = "insufficient_data"
        return {
            "parts": parts,
            "final_tree_health": final_health,
            "final_status": final_status,
            "critical_alert": critical_flag,
            "reason": f"Critical disease detected: {critical_reason}" if critical_flag else "No valid part predictions available."
        }

    # Weighted average of parts
    final_health = round(sum(valid_parts) / len(valid_parts), 2)
    final_status = "healthy" if final_health >= 50 else "unhealthy"

    # CRITICAL OVERRIDE - if any part has critical status, mark entire tree as critical
    if critical_flag:
        return {
            "parts": parts,
            "final_tree_health": final_health,   # still shown for report
            "final_status": "critical",  # Changed from "unhealthy" to "critical"
            "critical_alert": True,
            "reason": f"Critical disease detected: {critical_reason}"
        }

    # Normal return (no critical case)
    return {
        "parts": parts,
        "final_tree_health": final_health,
        "final_status": final_status,
        "critical_alert": False,
        "reason": "Tree status based on weighted average of all parts."
    }
