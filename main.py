from datetime import date, datetime
import json
import os
import uuid
import streamlit as st

# 1. საიტის კონფიგურაცია
st.set_page_config(page_title="My ToDo List", page_icon="📝", layout="wide")

# 🎨 CSS სტილები
st.markdown(
    """
<style>
    div[data-testid="stVerticalBlock"] > div {
        gap: 0.35rem !important;
    }
    div.stButton > button[kind="primary"] {
        background-color: #28a745 !important;
        color: white !important;
        border-color: #28a745 !important;
        border-radius: 6px;
        padding: 4px 12px;
        font-weight: 600;
        font-size: 13px;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #218838 !important;
        border-color: #1e7e34 !important;
        color: white !important;
    }
    div.stButton > button[kind="secondary"] {
        padding: 4px 10px;
        font-size: 13px;
        border-radius: 6px;
    }
    hr {
        margin: 6px 0px 8px 0px !important;
        border: 0;
        border-top: 1px solid rgba(255, 255, 255, 0.12);
    }
</style>
""",
    unsafe_allow_html=True,
)

# სათაური ცენტრში (შუაში)
st.markdown(
    "<h2 style='text-align: center; margin-bottom: 20px;'>📝 My ToDo List</h2>",
    unsafe_allow_html=True,
)

DB_FILE = "todos_db.json"

CATEGORIES = [
    "🏢 სამსახური",
    "👨‍👩‍👧 ოჯახი",
    "👤 პირადი",
    "🔄 ყოველთვიური დავალება",
    "📌 სხვა",
]


# -------------------------------------------------------------
# 2. ბაზასთან მუშაობის ფუნქციები (JSON Persistence)
# -------------------------------------------------------------
def load_todos() -> list[dict]:
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                if "category" not in item:
                    item["category"] = "📌 სხვა"
                if "is_monthly" not in item:
                    item["is_monthly"] = False
            return data
    except Exception:
        return []


def save_todos(todos: list[dict]) -> None:
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=4)


if "todos" not in st.session_state:
    st.session_state.todos = load_todos()


# -------------------------------------------------------------
# 3. ახალი დავალების დამატების ფორმა (განახლებული სტრუქტურა)
# -------------------------------------------------------------
st.markdown("#### ➕ ახალი დავალების დამატება")

with st.form("add_task_form", clear_on_submit=True):
    col_title, col_cat = st.columns([3, 2])

    with col_title:
        task_title = st.text_input(
            "დავალების ტექსტი", placeholder="რა გაქვთ გასაკეთებელი?"
        )

    with col_cat:
        # კატეგორიების ველი
        task_category = st.selectbox("აირჩიეთ კატეგორია", CATEGORIES)

        # 🎯 დედლაინის ველი: კომპაქტური, default=None (ცარიელი), ზუსტად კატეგორიის ქვემოთ
        deadline_date = st.date_input(
            "დედლაინი (არასავალდებულო)",
            value=None,
        )

    st.write("")
    _, col_btn_sub, _ = st.columns([2.5, 1.5, 2.5])
    with col_btn_sub:
        submitted = st.form_submit_button(
            "დავალების დამატება 🚀", use_container_width=True
        )

    if submitted:
        if task_title.strip():
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

            new_task = {
                "id": str(uuid.uuid4()),
                "title": task_title.strip(),
                "category": task_category,
                "created_at": now_str,
                # თუ თარიღი არ აირჩა, შეინახება როგორც None (დაბალი პრიორიტეტი)
                "deadline": (
                    deadline_date.strftime("%Y-%m-%d")
                    if deadline_date is not None
                    else None
                ),
                "is_completed": False,
                "completed_at": None,
                "is_monthly": (task_category == "🔄 ყოველთვიური დავალება"),
            }

            st.session_state.todos.append(new_task)
            save_todos(st.session_state.todos)
            st.success(f"დავალება დაემატა კატეგორიაში '{task_category}'!")
            st.rerun()
        else:
            st.warning("გთხოვთ, ჩაწეროთ დავალების ტექსტი!")

st.divider()


# -------------------------------------------------------------
# 4. დამხმარე ფუნქციები დავალებების გამოსატანად
# -------------------------------------------------------------
def get_deadline_badge(deadline_str: str):
    """ითვლის დედლაინს და აბრუნებს კომპაქტურ ბეიჯს."""
    if not deadline_str:
        return (
            "<span style='background-color: #2e7d32; color: white; padding: 3px 8px; border-radius: 5px; font-size: 11px; font-weight: 600;'>🟢 დაბალი პრიორიტეტი</span>",
            "სტატუსი:",
        )

    today = date.today()
    d_date = datetime.strptime(deadline_str, "%Y-%m-%d").date()
    days_left = (d_date - today).days

    if days_left < 0:
        badge = (
            f"<span style='background-color: #b71c1c; color: white; padding: 3px 8px; border-radius: 5px; font-size: 11px; font-weight: 600;'>"
            f"🚨 ვადაგადაცილებული ({abs(days_left)} დღით!)</span>"
        )
    elif days_left == 0:
        badge = (
            f"<span style='background-color: #e65100; color: white; padding: 3px 8px; border-radius: 5px; font-size: 11px; font-weight: 600;'>"
            f"🔥 დღესაა დედლაინი!</span>"
        )
    elif days_left <= 3:
        badge = (
            f"<span style='background-color: #d32f2f; color: white; padding: 3px 8px; border-radius: 5px; font-size: 11px; font-weight: 600;'>"
            f"🔴 დარჩა {days_left} დღე!</span>"
        )
    else:
        badge = (
            f"<span style='background-color: #0288d1; color: white; padding: 3px 8px; border-radius: 5px; font-size: 11px; font-weight: 600;'>"
            f"⏳ დარჩა {days_left} დღე</span>"
        )

    return badge, f"📅 {deadline_str}"


def render_active_task(task: dict, prefix: str):
    """გამოაქვს აქტიური დავალება მცირე შრიფტითა და მჭიდრო დაშორებით."""
    task_id = task["id"]
    badge, deadline_header = get_deadline_badge(task["deadline"])

    col_content, col_status, col_btn = st.columns([0.52, 0.32, 0.16])

    with col_content:
        st.markdown(
            f"<div style='font-size: 16px; font-weight: 600; margin-bottom: 2px; line-height: 1.2;'>{task['title']}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='font-size: 12px; color: #888888;'>🏷️ <code>{task.get('category', '📌 სხვა')}</code> | 🕒 {task['created_at']}</div>",
            unsafe_allow_html=True,
        )

    with col_status:
        st.markdown(
            f"<div style='text-align: center; font-size: 12px; line-height: 1.4; margin-top: 2px;'>"
            f"<b>{deadline_header}</b><br>{badge}</div>",
            unsafe_allow_html=True,
        )

    with col_btn:
        if st.button(
            "✅ დასრულება",
            key=f"done_{prefix}_{task_id}",
            type="primary",
            use_container_width=True,
        ):
            task["is_completed"] = True
            task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_todos(st.session_state.todos)
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)


def render_completed_task(task: dict, prefix: str):
    """გამოაქვს შესრულებული დავალება მჭიდროდ."""
    task_id = task["id"]
    col_content, col_del = st.columns([0.84, 0.16])

    with col_content:
        st.markdown(
            f"<div style='font-size: 15px; text-decoration: line-through; color: #777; margin-bottom: 2px;'>{task['title']}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='font-size: 12px; color: #888888;'>🏷️ <code>{task.get('category', '📌 სხვა')}</code> | 🕒 შექმნა: {task['created_at']} | ✅ <b>შესრულდა:</b> {task['completed_at']}</div>",
            unsafe_allow_html=True,
        )

    with col_del:
        if st.button(
            "🗑️ წაშლა", key=f"del_{prefix}_{task_id}", use_container_width=True
        ):
            st.session_state.todos = [
                t for t in st.session_state.todos if t["id"] != task_id
            ]
            save_todos(st.session_state.todos)
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)


def render_monthly_task(task: dict):
    """გამოაქვს ყოველთვიური დავალება მჭიდროდ წაშლის ღილაკით."""
    task_id = task["id"]
    badge, deadline_header = get_deadline_badge(task["deadline"])

    col_content, col_status, col_del = st.columns([0.52, 0.32, 0.16])

    with col_content:
        st.markdown(
            f"<div style='font-size: 16px; font-weight: 600; margin-bottom: 2px; line-height: 1.2;'>🔄 {task['title']}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='font-size: 12px; color: #888888;'>🏷️ <code>{task.get('category', '🔄 ყოველთვიური დავალება')}</code> | 🕒 {task['created_at']}</div>",
            unsafe_allow_html=True,
        )

    with col_status:
        st.markdown(
            f"<div style='text-align: center; font-size: 12px; line-height: 1.4; margin-top: 2px;'>"
            f"<b>{deadline_header}</b><br>{badge}</div>",
            unsafe_allow_html=True,
        )

    with col_del:
        if st.button(
            "🗑️ წაშლა", key=f"del_monthly_{task_id}", use_container_width=True
        ):
            st.session_state.todos = [
                t for t in st.session_state.todos if t["id"] != task_id
            ]
            save_todos(st.session_state.todos)
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)


# -------------------------------------------------------------
# 5. შესასრულებელი დავალებები (სტანდარტული კატეგორიები)
# -------------------------------------------------------------
st.markdown("#### 📌 შესასრულებელი დავალებები")

standard_active = [
    t
    for t in st.session_state.todos
    if not t["is_completed"]
    and t.get("category") != "🔄 ყოველთვიური დავალება"
    and not t.get("is_monthly", False)
]

STANDARD_TABS = ["🏢 სამსახური", "👨‍👩‍👧 ოჯახი", "👤 პირადი", "📌 სხვა"]

if not standard_active:
    st.info("აქტიური დავალებები არ გაქვთ. ყველაფერი შესრულებულია! ☕")
else:
    tabs = st.tabs(["🌐 ყველა"] + STANDARD_TABS)

    with tabs[0]:
        for t in standard_active:
            render_active_task(t, prefix="all")

    for idx, cat_name in enumerate(STANDARD_TABS, start=1):
        with tabs[idx]:
            cat_tasks = [
                t
                for t in standard_active
                if t.get("category", "📌 სხვა") == cat_name
            ]
            if cat_tasks:
                for t in cat_tasks:
                    render_active_task(t, prefix=f"cat_{idx}")
            else:
                st.caption(f"კატეგორიაში '{cat_name}' დავალებები არ არის.")

st.divider()

# -------------------------------------------------------------
# 6. შესრულებული დავალებები
# -------------------------------------------------------------
st.markdown("#### ✅ შესრულებული დავალებები")

completed_todos = [
    t
    for t in st.session_state.todos
    if t["is_completed"] and t.get("category") != "🔄 ყოველთვიური დავალება"
]

if not completed_todos:
    st.caption("შესრულებული დავალებების სია ჯერ ცარიელია.")
else:
    comp_tabs = st.tabs(["🌐 ყველა"] + STANDARD_TABS)

    with comp_tabs[0]:
        for t in completed_todos:
            render_completed_task(t, prefix="comp_all")

    for idx, cat_name in enumerate(STANDARD_TABS, start=1):
        with comp_tabs[idx]:
            cat_comp = [
                t
                for t in completed_todos
                if t.get("category", "📌 სხვა") == cat_name
            ]
            if cat_comp:
                for t in cat_comp:
                    render_completed_task(t, prefix=f"comp_cat_{idx}")
            else:
                st.caption(
                    f"კატეგორიაში '{cat_name}' შესრულებული დავალებები არ არის."
                )

st.divider()

# -------------------------------------------------------------
# 7. ყოველთვიური დავალებები (ცალკე გამოყოფილი ბლოკი)
# -------------------------------------------------------------
st.markdown("#### 🔄 ყოველთვიური დავალებები")

monthly_todos = [
    t
    for t in st.session_state.todos
    if t.get("category") == "🔄 ყოველთვიური დავალება"
    or t.get("is_monthly", False)
]

if not monthly_todos:
    st.caption("ყოველთვიური რუტინული დავალებები ჯერ არ გაქვთ დამატებული.")
else:
    for t in monthly_todos:
        render_monthly_task(t)