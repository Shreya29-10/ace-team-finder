import pandas as pd

WEIGHTS = {"complementarity": 0.40, "skill_fit": 0.25,
           "interests": 0.20, "availability": 0.15}


def to_map(text):
    """'Python; ML' -> {'python': 'Python', 'ml': 'ML'} (lowercase key, original naam value)"""
    return {x.strip().lower(): x.strip() for x in str(text).split(";") if x.strip()}


def complementarity(role, required_roles, team_roles):
    role = role.lower()
    missing = required_roles - team_roles
    if role in missing:
        return 1.0
    if role in required_roles:
        return 0.3
    return 0.1


def skill_fit(cand_skills, req_skills):
    return min(1.0, len(cand_skills & req_skills) / 2)


def interest_score(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def availability_score(a, b):
    a, b = a.lower(), b.lower()
    if a == b:
        return 1.0
    if "flexible" in (a, b):
        return 0.8
    return 0.2


def score_candidate(me, cand, event, team_roles):
    req_roles = set(to_map(event["required_roles"]))
    req_skills_map = to_map(event["required_skills"])
    cand_skills_map = to_map(cand["skills"])
    my_int, cand_int = to_map(me["interests"]), to_map(cand["interests"])

    comp = complementarity(cand["preferred_role"], req_roles, team_roles)
    common_skills = set(cand_skills_map) & set(req_skills_map)
    fit = skill_fit(set(cand_skills_map), set(req_skills_map))
    common_int = set(my_int) & set(cand_int)
    inter = interest_score(set(my_int), set(cand_int))
    avail = availability_score(me["availability"], cand["availability"])

    total = (WEIGHTS["complementarity"] * comp + WEIGHTS["skill_fit"] * fit
             + WEIGHTS["interests"] * inter + WEIGHTS["availability"] * avail)

    # "Why this match?" ke reasons
    why = []
    if comp == 1.0:
        why.append(f"fills the missing {cand['preferred_role']} role")
    elif comp == 0.3:
        why.append(f"same role as your team ({cand['preferred_role']})")
    if common_skills:
        why.append("knows " + ", ".join(cand_skills_map[s] for s in common_skills) + " (needed for event)")
    if common_int:
        why.append("shared interest in " + ", ".join(cand_int[i] for i in common_int))
    if avail == 1.0:
        why.append(f"both free {cand['availability'].lower()}")
    elif avail == 0.8:
        why.append("flexible schedule")
    if cand["college"] != me["college"]:
        why.append(f"from {cand['college']} (cross-college)")

    return {
        "id": cand["id"], "name": cand["name"], "preferred_role": cand["preferred_role"],
        "college": cand["college"], "match": round(total * 100),
        "why": "; ".join(why) if why else "general profile compatibility",
        "complementarity": comp, "skill_fit": fit, "interests": inter, "availability": avail,
    }


def rank_matches(me, event, profiles, team_roles=None, top_n=5):
    """me = ek profile row, event = ek event row, profiles = poori DataFrame."""
    team_roles = {r.lower() for r in (team_roles or [me["preferred_role"]])}
    pool = profiles[(profiles["visibility"] == "public") & (profiles["id"] != me["id"])]
    results = [score_candidate(me, row, event, team_roles) for _, row in pool.iterrows()]
    return pd.DataFrame(results).sort_values("match", ascending=False).head(top_n).reset_index(drop=True)