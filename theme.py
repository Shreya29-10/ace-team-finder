import streamlit as st

PAGES = ["Dashboard", "Find Teammates", "Invites", "My Team", "My Privacy",
         "Browse Students", "Create My Profile"]
LABELS = {"Dashboard": "🏠  Dashboard", "Find Teammates": "🔍  Find Teammates",
          "Invites": "✉️  Invites", "My Team": "👥  My Team", "My Privacy": "🔒  My Privacy",
          "Browse Students": "📇  Browse Students", "Create My Profile": "➕  Create My Profile"}
GRAD = {"purple": "linear-gradient(135deg,#7C3AED,#4F46E5)", "pink": "linear-gradient(135deg,#EC4899,#8B5CF6)",
        "orange": "linear-gradient(135deg,#F59E0B,#EF4444)", "blue": "linear-gradient(135deg,#06B6D4,#3B82F6)"}
ICON = {"ml/data": "🧠", "frontend/web": "💻", "backend": "⚙️", "ui-ux": "🎨",
        "presenter/research": "🎤", "iot/hardware": "🔌"}
TITLES = ["Rookie", "Explorer", "Connector", "Team Builder", "Squad Leader", "Legend"]

CSS = """
.stApp{background:radial-gradient(circle at 12% 8%,#3b1d6e 0%,#150a30 45%,#0b0618 100%);}
[data-testid="stSidebar"]{background:rgba(10,5,25,.85);border-right:1px solid rgba(255,255,255,.08);}
[data-testid="stVerticalBlockBorderWrapper"]{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.12)!important;border-radius:18px;}
[data-testid="stMetric"]{background:linear-gradient(135deg,rgba(139,92,246,.35),rgba(236,72,153,.22));border:1px solid rgba(255,255,255,.15);border-radius:16px;padding:10px 16px;}
.stButton>button,.stFormSubmitButton>button{border-radius:999px;border:0;font-weight:700;color:#fff;background:linear-gradient(90deg,#8B5CF6,#EC4899);transition:.15s;}
.stButton>button:hover,.stFormSubmitButton>button:hover{transform:translateY(-2px) scale(1.03);box-shadow:0 6px 18px rgba(236,72,153,.4);color:#fff;}
.stProgress>div>div>div>div{background:linear-gradient(90deg,#8B5CF6,#EC4899,#F59E0B);}
[data-testid="stSidebar"] label[data-baseweb="radio"]{padding:8px 12px;border-radius:12px;}
[data-testid="stSidebar"] label[data-baseweb="radio"]:hover{background:rgba(139,92,246,.25);}
.hero{padding:22px 28px;border-radius:22px;margin-bottom:14px;background:linear-gradient(120deg,rgba(124,58,237,.55),rgba(236,72,153,.4),rgba(245,158,11,.35));border:1px solid rgba(255,255,255,.18);}
.hero h1{margin:0;font-size:2rem;} .hero p{margin:4px 0 0;opacity:.9;}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;margin:8px 0 14px;}
.gcard{border-radius:20px;padding:16px 18px;color:#fff;box-shadow:0 8px 24px rgba(0,0,0,.35);}
.gcard small{opacity:.85;} .gcard h2{margin:2px 0;font-size:2rem;}
.slots{display:flex;gap:12px;flex-wrap:wrap;margin:10px 0 16px;}
.slot{min-width:120px;text-align:center;padding:12px 10px;border-radius:18px;background:linear-gradient(135deg,rgba(124,58,237,.6),rgba(79,70,229,.45));border:1px solid rgba(255,255,255,.25);}
.slot.empty{background:transparent;border:2px dashed rgba(255,255,255,.35);opacity:.85;}
.slot span{font-size:1.8rem;display:block;} .slot b{font-size:.85rem;}
.badge{display:inline-block;margin:4px 6px 4px 0;padding:8px 12px;border-radius:999px;font-size:.85rem;font-weight:600;background:linear-gradient(90deg,#F59E0B,#EC4899);}
.badge.off{background:rgba(255,255,255,.08);opacity:.55;filter:grayscale(1);}
.player{padding:14px;border-radius:18px;background:linear-gradient(135deg,rgba(124,58,237,.5),rgba(236,72,153,.35));border:1px solid rgba(255,255,255,.2);margin-bottom:10px;}
.xpbar{height:8px;border-radius:99px;background:rgba(255,255,255,.2);margin-top:8px;overflow:hidden;}
.xpbar i{display:block;height:100%;background:linear-gradient(90deg,#FDE68A,#F59E0B);}
"""


NAV_CSS = """
header[data-testid="stHeader"]{background:transparent;} #MainMenu{visibility:hidden;} footer{visibility:hidden;}
[data-testid="stSidebar"] [role="radiogroup"]{gap:4px;}
[data-testid="stSidebar"] label[data-baseweb="radio"]{width:100%;margin:0;padding:11px 14px;border-radius:12px;border-left:3px solid transparent;transition:.15s;}
[data-testid="stSidebar"] label[data-baseweb="radio"]>div:first-child{display:none;}
[data-testid="stSidebar"] label[data-baseweb="radio"]:hover{background:rgba(139,92,246,.22);}
[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked){background:linear-gradient(90deg,rgba(139,92,246,.55),rgba(236,72,153,.3));border-left:3px solid #F59E0B;font-weight:700;}
[data-testid="stSidebar"] label[data-baseweb="radio"] p{font-size:.98rem;}
.brand{display:flex;gap:12px;align-items:center;padding:4px 4px 16px;margin-bottom:14px;border-bottom:1px solid rgba(255,255,255,.1);}
.logo{width:42px;height:42px;border-radius:12px;display:grid;place-items:center;font-size:1.4rem;background:linear-gradient(135deg,#8B5CF6,#EC4899);}
.navlabel{font-size:.7rem;letter-spacing:.12em;opacity:.55;margin:0 0 6px 6px;}
"""
BRAND = '<div class="brand"><div class="logo">🤝</div><div><b>ACE Team Finder</b><br><small>Find. Match. Build.</small></div></div><div class="navlabel">MENU</div>'
CSS += NAV_CSS


def inject_css():
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


def stat_card(title, value, sub, color):
    return f'<div class="gcard" style="background:{GRAD[color]}"><small>{title}</small><h2>{value}</h2><small>{sub}</small></div>'


def cards_row(cards):
    st.markdown('<div class="grid">' + "".join(cards) + "</div>", unsafe_allow_html=True)


def slots_html(size, members, roles_of, req_roles):
    roles = [roles_of[m] for m in members]
    covered = {r.lower() for r in roles}
    missing = [r for r in req_roles if r.lower() not in covered]
    out = ""
    for r in roles:
        out += f'<div class="slot"><span>{ICON.get(r.lower(), "🙂")}</span><b>{r}</b></div>'
    for i in range(max(size - len(roles), 0)):
        r = missing[i] if i < len(missing) else "Open slot"
        out += f'<div class="slot empty"><span>❓</span><b>{r}</b></div>'
    return f'<div class="slots">{out}</div>'


def xp_stats(df, inv, tasks, me):
    if me is None:
        return None
    sent, got = inv[inv["from_id"] == me], inv[inv["to_id"] == me]
    acc = inv[(inv["status"] == "Accepted") & ((inv["from_id"] == me) | (inv["to_id"] == me))]
    done = int(((tasks["assigned_to"] == me) & tasks["done"]).sum())
    col = dict(zip(df["id"], df["college"]))
    cross = any(col.get(r["to_id"] if r["from_id"] == me else r["from_id"]) != col.get(me)
                for _, r in acc.iterrows())
    xp = 50 + 10 * len(sent) + 25 * len(acc) + 15 * done
    level = xp // 100 + 1
    quests = [("Complete your profile", 50, True), ("Send your first invite", 10, len(sent) > 0),
              ("Get a teammate to accept", 25, len(acc) > 0), ("Finish a team task", 15, done > 0)]
    badges = [("🚀", "First Invite", len(sent) > 0), ("🤝", "Team Up", len(acc) > 0),
              ("🌍", "Cross-College", cross), ("✅", "Task Master", done >= 3), ("⭐", "Level 3", level >= 3)]
    return {"xp": xp, "level": level, "into": xp % 100, "sent": len(sent), "accepted": len(acc),
            "tasks_done": done, "title": TITLES[min(level - 1, len(TITLES) - 1)],
            "quests": quests, "badges": badges}


def badges_html(badges):
    return "".join(f'<span class="badge{"" if ok else " off"}">{e} {n}</span>' for e, n, ok in badges)


def player_card(S, name):
    return (f'<div class="player"><b>{name}</b><br>{S["title"]} · Level {S["level"]}'
            f'<div class="xpbar"><i style="width:{S["into"]}%"></i></div>'
            f'<small>{S["xp"]} XP</small></div>')
