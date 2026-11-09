import os
import streamlit as st
import pandas as pd
from matching import rank_matches, to_map
from theme import *

st.set_page_config(page_title="ACE Team Finder", page_icon="🤝", layout="wide")
inject_css()

PROFILES = "profiles.csv"
EVENTS = "events.csv"
INVITES = "invites.csv"
TASKS = "tasks.csv"
INVITE_COLS = ["invite_id", "event_name", "from_id", "to_id", "status"]
TASK_COLS = ["task_id", "event_name", "leader_id", "task", "assigned_to", "done"]


def load_profiles():
    return pd.read_csv(PROFILES)


def load_events():
    return pd.read_csv(EVENTS)


def all_skills(df):
    return sorted({s.strip() for x in df["skills"] for s in x.split(";")})


def all_interests(df):
    return sorted({s.strip() for x in df["interests"] for s in x.split(";")})


def save_profile(row):
    df = load_profiles()
    row["id"] = int(df["id"].max()) + 1
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(PROFILES, index=False)
    return row["id"]


def set_visibility(profile_id, visibility):
    d = load_profiles()
    d.loc[d["id"] == profile_id, "visibility"] = visibility
    d.to_csv(PROFILES, index=False)


# ----------------------------------------------------------- invites helpers
def load_invites():
    types = {"invite_id": int, "from_id": int, "to_id": int}
    if not os.path.exists(INVITES):
        return pd.DataFrame(columns=INVITE_COLS).astype(types)
    return pd.read_csv(INVITES).astype(types)


def get_invite(event_name, from_id, to_id):
    inv = load_invites()
    m = inv[(inv["event_name"] == event_name) & (inv["from_id"] == from_id)
            & (inv["to_id"] == to_id)]
    return None if m.empty else m.iloc[0]


def send_invite(event_name, from_id, to_id):
    if get_invite(event_name, from_id, to_id) is not None:
        return False
    inv = load_invites()
    new_id = 1 if inv.empty else int(inv["invite_id"].max()) + 1
    inv.loc[len(inv)] = [new_id, event_name, from_id, to_id, "Pending"]
    inv.to_csv(INVITES, index=False)
    return True


def set_status(invite_id, status):
    inv = load_invites()
    inv.loc[inv["invite_id"] == invite_id, "status"] = status
    inv.to_csv(INVITES, index=False)


# ----------------------------------------------------------- team helpers
def team_members(event_name, leader_id):
    """Leader + everyone who accepted the leader's invite for this event."""
    inv = load_invites()
    acc = inv[(inv["event_name"] == event_name) & (inv["from_id"] == leader_id)
              & (inv["status"] == "Accepted")]
    return [int(leader_id)] + [int(x) for x in acc["to_id"]]


def my_teams(me_id):
    """All (event, leader) teams where I am the leader or a member."""
    acc = load_invites()
    acc = acc[acc["status"] == "Accepted"]
    teams = set()
    for _, r in acc.iterrows():
        if r["from_id"] == me_id or r["to_id"] == me_id:
            teams.add((r["event_name"], int(r["from_id"])))
    return sorted(teams)


# ----------------------------------------------------------- tasks helpers
def load_tasks():
    types = {"task_id": int, "leader_id": int, "assigned_to": int, "done": bool}
    if not os.path.exists(TASKS):
        return pd.DataFrame(columns=TASK_COLS).astype(types)
    return pd.read_csv(TASKS).astype(types)


def add_task(event_name, leader_id, task, assigned_to):
    t = load_tasks()
    new_id = 1 if t.empty else int(t["task_id"].max()) + 1
    t.loc[len(t)] = [new_id, event_name, leader_id, task, assigned_to, False]
    t.to_csv(TASKS, index=False)


def set_task_done(task_id, done):
    t = load_tasks()
    t.loc[t["task_id"] == task_id, "done"] = done
    t.to_csv(TASKS, index=False)


ICON = {"Pending": "🕒", "Accepted": "✅", "Declined": "❌"}

st.markdown('<div class="hero"><h1>🤝 ACE Team Finder</h1><p>Find your dream team. Level up together.</p></div>', unsafe_allow_html=True)
st.caption("AI-powered team matching for AllCollegeEvent · demo with sample data only")
st.sidebar.markdown(BRAND, unsafe_allow_html=True)
page = st.sidebar.radio("Navigate", PAGES, format_func=lambda k: LABELS[k], label_visibility="collapsed")
df = load_profiles()
names = dict(zip(df["id"], df["name"]))
roles_of = dict(zip(df["id"], df["preferred_role"]))

me_now = st.session_state.get("me")
if me_now is not None:
    _inv = load_invites()
    n_pending = int(((_inv["to_id"] == me_now) & (_inv["status"] == "Pending")).sum())
    if n_pending:
        st.sidebar.info(f"📥 {n_pending} pending invite(s). Open 'Invites'.")


_S = xp_stats(df, load_invites(), load_tasks(), st.session_state.get("me"))
if _S:
    st.sidebar.markdown(player_card(_S, names.get(st.session_state.get("me"), "")), unsafe_allow_html=True)


def pick_me(label, key):
    ids = df["id"].tolist()
    idx = ids.index(st.session_state["me"]) if st.session_state.get("me") in ids else 0
    me_id = st.selectbox(label, ids, index=idx, key=key,
                         format_func=lambda i: f"{names[i]}  ({roles_of[i]})")
    st.session_state["me"] = me_id
    return int(me_id)


# ---------------------------------------------------------------- Find Teammates
if page == "Dashboard":
    inv, tk = load_invites(), load_tasks()
    pub = df[df["visibility"] == "public"]
    me_id = pick_me("Playing as", "me_dash")
    S = xp_stats(df, inv, tk, me_id)
    cards_row([
        stat_card("Students", len(pub), "public profiles", "purple"),
        stat_card("Events", len(load_events()), "open to join", "pink"),
        stat_card("My invites", S["sent"], f"{S['accepted']} accepted", "orange"),
        stat_card("Tasks done", S["tasks_done"], "keep going!", "blue"),
    ])
    c1, c2 = st.columns([3, 2])
    with c1:
        st.subheader(f"{S['title']} · Level {S['level']}")
        st.progress(S["into"] / 100)
        st.caption(f"{S['xp']} XP · {100 - S['into']} XP to next level")
        st.subheader("🎯 Quests")
        for text, xp, ok in S["quests"]:
            st.markdown(f"{'✅' if ok else '⬜'} {text} · **+{xp} XP**")
    with c2:
        st.subheader("🏅 Badges")
        st.markdown(badges_html(S["badges"]), unsafe_allow_html=True)
    st.subheader("📊 Students by role")
    st.bar_chart(pub["preferred_role"].value_counts(), color="#A78BFA")

elif page == "Find Teammates":
    st.header("Find Teammates for an Event")
    events = load_events()

    ev_name = st.selectbox("Select an event", events["event_name"])
    event = events[events["event_name"] == ev_name].iloc[0]
    req_roles = list(to_map(event["required_roles"]).values())
    req_skills = list(to_map(event["required_skills"]).values())

    c1, c2, c3 = st.columns(3)
    c1.metric("Type", event["type"].title())
    c2.metric("Team size", int(event["team_size"]))
    c3.metric("Date", str(event["date"]))
    st.markdown("**Roles needed:** " + "  ".join(f"`{r}`" for r in req_roles))
    st.markdown("**Skills needed:** " + "  ".join(f"`{s}`" for s in req_skills))

    st.divider()

    me_id = pick_me("You are", "me_find")
    me = df[df["id"] == me_id].iloc[0]

    members = team_members(ev_name, me_id)
    if len(members) > 1:
        st.caption(f"✅ {len(members) - 1} teammate(s) already joined your team for this event.")
    default_roles = sorted({roles_of[m] for m in members})
    team_roles = st.multiselect(
        "Roles already in your team", sorted(df["preferred_role"].unique()),
        default=default_roles, key=f"tr_{ev_name}_{me_id}_{len(members)}")
    missing = [r for r in req_roles if r.lower() not in {t.lower() for t in team_roles}]
    if missing:
        st.warning("Still missing: " + ", ".join(missing))
    else:
        st.success("Your team already covers all required roles. Showing best overall matches.")

    st.markdown("**Your dream team**")
    st.markdown(slots_html(int(event["team_size"]), members, roles_of, req_roles), unsafe_allow_html=True)
    top_n = st.slider("How many matches?", 3, 10, 5)

    st.subheader("🔍 AI Recommended Teammates")
    matches = rank_matches(me, event, df, team_roles=team_roles, top_n=top_n)

    for _, r in matches.iterrows():
        cand_id = int(r["id"])
        with st.container(border=True):
            left, right = st.columns([4, 1])
            left.markdown(f"### {r['name']}")
            left.caption(f"{r['preferred_role']}  ·  {r['college']}")
            right.metric("Match", f"{r['match']}%")
            st.progress(int(r["match"]) / 100)
            st.markdown(f"💡 **Why this match?** {r['why']}")
            with st.expander("Score breakdown"):
                b1, b2, b3, b4 = st.columns(4)
                for col, label, key in [
                    (b1, "Complementarity (40%)", "complementarity"),
                    (b2, "Skill fit (25%)", "skill_fit"),
                    (b3, "Interests (20%)", "interests"),
                    (b4, "Availability (15%)", "availability"),
                ]:
                    col.caption(label)
                    col.progress(float(r[key]))

            existing = get_invite(ev_name, me_id, cand_id)
            if existing is not None:
                st.info(f"{ICON[existing['status']]} Invite {existing['status']}")
            elif st.button("✉️ Send Invite", key=f"inv_{ev_name}_{me_id}_{cand_id}"):
                send_invite(ev_name, me_id, cand_id)
                st.rerun()

# ---------------------------------------------------------------- Invites
elif page == "Invites":
    st.header("Invites")
    me_id = pick_me("View invites as", "me_inv")
    inv = load_invites()

    tab_recv, tab_sent = st.tabs(["📥 Received", "📤 Sent"])

    with tab_recv:
        recv = inv[inv["to_id"] == me_id]
        if recv.empty:
            st.caption("No invites received yet.")
        for _, row in recv.iterrows():
            with st.container(border=True):
                st.markdown(
                    f"**{names[row['from_id']]}** ({roles_of[row['from_id']]}) invited you "
                    f"to join their team for **{row['event_name']}**")
                if row["status"] == "Pending":
                    a, b, _ = st.columns([1, 1, 4])
                    if a.button("✅ Accept", key=f"acc_{row['invite_id']}"):
                        set_status(row["invite_id"], "Accepted")
                        st.rerun()
                    if b.button("❌ Decline", key=f"dec_{row['invite_id']}"):
                        set_status(row["invite_id"], "Declined")
                        st.rerun()
                else:
                    st.write(f"{ICON[row['status']]} {row['status']}")

    with tab_sent:
        sent = inv[inv["from_id"] == me_id]
        if sent.empty:
            st.caption("You have not sent any invites yet.")
        else:
            view = pd.DataFrame({
                "Event": sent["event_name"],
                "Invited": sent["to_id"].map(names),
                "Role": sent["to_id"].map(roles_of),
                "Status": sent["status"].map(lambda s: f"{ICON[s]} {s}"),
            })
            st.dataframe(view, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------- My Team
elif page == "My Team":
    st.header("My Team")
    me_id = pick_me("View team as", "me_team")
    teams = my_teams(me_id)

    if not teams:
        st.info("No team yet. Send an invite from 'Find Teammates' and ask the student "
                "to accept it in 'Invites'.")
    else:
        events = load_events()
        ev_name, leader = st.selectbox(
            "Select team", teams, format_func=lambda t: f"{t[0]}  (led by {names[t[1]]})")
        event = events[events["event_name"] == ev_name].iloc[0]
        members = team_members(ev_name, leader)
        size = int(event["team_size"])

        c1, c2, c3 = st.columns(3)
        c1.metric("Event", ev_name)
        c2.metric("Members", f"{len(members)} / {size}")
        c3.metric("Date", str(event["date"]))
        st.progress(min(len(members) / size, 1.0))
        st.markdown(slots_html(size, members, roles_of, list(to_map(event["required_roles"]).values())),
                    unsafe_allow_html=True)
        if len(members) >= size and not st.session_state.get(f"cel_{ev_name}_{leader}"):
            st.balloons()
            st.session_state[f"cel_{ev_name}_{leader}"] = True

        mem = df[df["id"].isin(members)].copy()
        mem["position"] = mem["id"].map(lambda i: "👑 Leader" if i == leader else "Member")
        st.dataframe(
            mem[["name", "position", "preferred_role", "college", "skills"]]
            .rename(columns={"preferred_role": "role"}),
            use_container_width=True, hide_index=True)

        covered = {roles_of[m].lower() for m in members}
        req_roles = list(to_map(event["required_roles"]).values())
        missing = [r for r in req_roles if r.lower() not in covered]
        if missing:
            st.warning("Still missing roles: " + ", ".join(missing)
                       + ". Use 'Find Teammates' to invite them.")
        else:
            st.success("All required roles are covered 🎉")
        if len(members) >= size:
            st.success("Team is full.")

        st.divider()
        st.subheader("📋 Team tasks")
        tasks = load_tasks()
        mine = tasks[(tasks["event_name"] == ev_name) & (tasks["leader_id"] == leader)]

        with st.form("task_form", clear_on_submit=True):
            t1, t2 = st.columns([3, 1])
            text = t1.text_input("New task")
            assignee = t2.selectbox("Assign to", members, format_func=lambda i: names[i])
            if st.form_submit_button("Add task") and text.strip():
                add_task(ev_name, leader, text.strip(), int(assignee))
                st.rerun()

        if mine.empty:
            if st.button("Add sample tasks"):
                for i, task in enumerate(["Finalize idea", "Design wireframes", "Build prototype"]):
                    add_task(ev_name, leader, task, members[i % len(members)])
                st.rerun()
        else:
            done_count = int(mine["done"].sum())
            st.caption(f"{done_count} of {len(mine)} tasks done")
            st.progress(done_count / len(mine))
            for _, row in mine.iterrows():
                c1, c2 = st.columns([6, 2])
                checked = c1.checkbox(row["task"], value=bool(row["done"]), key=f"task_{row['task_id']}")
                c2.caption(f"👤 {names[row['assigned_to']]}")
                if checked != bool(row["done"]):
                    set_task_done(row["task_id"], checked)
                    st.rerun()

# ---------------------------------------------------------------- My Privacy
elif page == "My Privacy":
    st.header("🔒 My Privacy & Consent")
    me_id = pick_me("Manage privacy for", "me_priv")
    me = df[df["id"] == me_id].iloc[0]
    is_public = me["visibility"] == "public"

    new_val = st.toggle("Let other students find my profile", value=is_public, key=f"vis_{me_id}")
    if new_val != is_public:
        set_visibility(me_id, "public" if new_val else "private")
        st.rerun()

    if is_public:
        st.success("Your profile is public. It appears in 'Browse Students' and in AI matches.")
    else:
        st.warning("Your profile is private. It is hidden from 'Browse Students' and from AI matches. "
                   "You can still find teammates and send invites yourself.")

    st.subheader("What other students can see")
    st.dataframe(
        me[["name", "college", "year", "skills", "interests", "preferred_role", "availability"]]
        .to_frame("value"), use_container_width=True)
    st.caption("No email or phone number is collected. A team forms only when the invited "
               "student accepts the invite.")

# ---------------------------------------------------------------- Browse
elif page == "Browse Students":
    st.header("Browse Students")
    pub = df[df["visibility"] == "public"]
    c1, c2, c3 = st.columns(3)
    colleges = c1.multiselect("College", sorted(pub["college"].unique()))
    roles = c2.multiselect("Preferred role", sorted(pub["preferred_role"].unique()))
    skill = c3.text_input("Skill contains")
    if colleges:
        pub = pub[pub["college"].isin(colleges)]
    if roles:
        pub = pub[pub["preferred_role"].isin(roles)]
    if skill:
        pub = pub[pub["skills"].str.contains(skill, case=False)]
    st.caption(f"{len(pub)} students found")
    st.dataframe(pub.drop(columns=["visibility"]), use_container_width=True, hide_index=True)

# ---------------------------------------------------------------- Create profile
else:
    st.header("Create My Profile")
    with st.form("profile_form"):
        name = st.text_input("Full name")
        college = st.text_input("College")
        year = st.selectbox("Year", ["FE", "SE", "TE", "BE"])
        skills = st.multiselect("Skills", all_skills(df))
        level = st.selectbox("Experience level", ["Beginner", "Intermediate", "Advanced"])
        interests = st.multiselect("Interests", all_interests(df))
        role = st.selectbox("Preferred role", sorted(df["preferred_role"].unique()))
        avail = st.selectbox("Availability", ["Weekends", "Evenings", "Flexible"])
        past = st.number_input("Past hackathons", 0, 20, 0)
        consent = st.checkbox("I allow other students to see my profile", value=True)
        submitted = st.form_submit_button("Save profile")

    if submitted:
        if not name or not college or not skills or not interests:
            st.error("Please fill name, college, skills and interests.")
        else:
            new_id = save_profile({
                "name": name, "college": college, "year": year,
                "skills": "; ".join(skills), "experience_level": level,
                "interests": "; ".join(interests), "preferred_role": role,
                "availability": avail, "past_hackathons": int(past),
                "visibility": "public" if consent else "private",
            })
            st.session_state["me"] = new_id
            st.success(f"Profile saved! Your ID is {new_id}. Go to 'Find Teammates' to see your matches.")
