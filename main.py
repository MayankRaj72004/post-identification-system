import streamlit as st
from streamlit_option_menu import option_menu

import address_parsing
import dashboard
import handwritten_recognition
import home
import home1
import pin_code_correction
import route_optimization
import voice_address_recognition
import wrong_pincode_storage

# Set page configuration
st.set_page_config(
    page_title="AI Postal System Optimizer",
    page_icon="📮",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─── Global CSS: Premium Dark Theme ─────────────────────────────────────────
def render_dark_theme():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        /* ── Global ── */
        .stApp {
            background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 40%, #16213e 100%);
            color: #e0e0e0;
            font-family: 'Inter', sans-serif;
        }

        /* ── Sidebar ── */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0d1117 0%, #161b22 100%) !important;
            border-right: 1px solid rgba(56, 189, 248, 0.15);
        }
        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] .stMarkdown span {
            color: #c9d1d9 !important;
        }

        /* ── Header bar ── */
        .header-bar {
            background: rgba(15, 12, 41, 0.85);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba(56, 189, 248, 0.2);
            padding: 12px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 1000;
            border-radius: 0 0 12px 12px;
        }
        .header-bar a {
            color: #94a3b8;
            text-decoration: none;
            font-size: 15px;
            font-weight: 500;
            padding: 8px 18px;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        .header-bar a:hover {
            background: rgba(56, 189, 248, 0.15);
            color: #38bdf8;
        }

        /* ── Cards / Containers ── */
        .glass-card {
            background: rgba(255, 255, 255, 0.04);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 28px;
            margin-bottom: 20px;
            transition: transform 0.25s ease, box-shadow 0.25s ease;
        }
        .glass-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 32px rgba(56, 189, 248, 0.12);
        }

        /* ── Metric Cards ── */
        .metric-card {
            background: linear-gradient(135deg, rgba(56,189,248,0.12) 0%, rgba(139,92,246,0.08) 100%);
            border: 1px solid rgba(56, 189, 248, 0.2);
            border-radius: 14px;
            padding: 22px;
            text-align: center;
        }
        .metric-value {
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 6px 0;
        }
        .metric-label {
            font-size: 0.85rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            font-weight: 600;
        }

        /* ── Section Titles ── */
        .section-title {
            font-size: 1.6rem;
            font-weight: 700;
            background: linear-gradient(135deg, #38bdf8, #818cf8, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 6px;
        }
        .section-subtitle {
            color: #64748b;
            font-size: 0.95rem;
            margin-bottom: 22px;
        }

        /* ── Buttons ── */
        .stButton > button {
            background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
            color: white !important;
            border: none;
            border-radius: 10px;
            padding: 10px 28px;
            font-weight: 600;
            font-size: 15px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
        }
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(37, 99, 235, 0.45);
        }

        /* ── Input Fields ── */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(56, 189, 248, 0.2) !important;
            border-radius: 10px !important;
            color: #e0e0e0 !important;
        }
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus {
            border-color: #38bdf8 !important;
            box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.15) !important;
        }

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 6px;
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            padding: 4px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            color: #94a3b8;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            background: rgba(56, 189, 248, 0.15) !important;
            color: #38bdf8 !important;
        }

        /* ── Dataframe ── */
        .stDataFrame {
            border-radius: 12px;
            overflow: hidden;
        }

        /* ── Success / Error / Info / Warning ── */
        .stSuccess, .stInfo, .stWarning, .stError {
            border-radius: 10px !important;
        }

        /* ── Divider ── */
        hr {
            border-color: rgba(56, 189, 248, 0.1) !important;
        }

        /* ── Scrollbar ── */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #0d1117; }
        ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #484f58; }

        /* ── Status badge ── */
        .status-correct {
            background: rgba(34, 197, 94, 0.15);
            color: #22c55e;
            padding: 4px 14px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85rem;
            display: inline-block;
        }
        .status-incorrect {
            background: rgba(239, 68, 68, 0.15);
            color: #ef4444;
            padding: 4px 14px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85rem;
            display: inline-block;
        }
        .status-corrected {
            background: rgba(56, 189, 248, 0.15);
            color: #38bdf8;
            padding: 4px 14px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85rem;
            display: inline-block;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )


# ─── Header ─────────────────────────────────────────────────────────────────
def render_header():
    st.markdown(
        """
        <div class="header-bar">
            <div style="display:flex;align-items:center;gap:10px;">
                <span style="font-size:24px;">📮</span>
                <span style="font-size:18px;font-weight:700;
                      background:linear-gradient(135deg,#38bdf8,#818cf8);
                      -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                    AI Postal Optimizer
                </span>
            </div>
            <div>
                <a href="#">About</a>
                <a href="#">Services</a>
                <a href="#">Contact</a>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )


# ─── Main Application ───────────────────────────────────────────────────────
def run_main_app():
    render_header()

    with st.sidebar:
        selected_page = option_menu(
            menu_title="📮 Postal Optimizer",
            options=[
                "Home",
                "Validate Pincode",
                "Handwritten Address Recognition",
                "Voice-Based Address Recognition",
                "Address Parsing",
                "Wrong Pincode Storage",
                "Route Optimization",
                "Dashboard",
            ],
            icons=[
                "house-fill",
                "check-circle-fill",
                "pencil-fill",
                "mic-fill",
                "folder-fill",
                "file-earmark-excel-fill",
                "map-fill",
                "graph-up-arrow",
            ],
            menu_icon="mailbox2",
            default_index=0,
            styles={
                "container": {"padding": "8px", "background-color": "transparent"},
                "icon": {"color": "#38bdf8", "font-size": "18px"},
                "nav-link": {
                    "color": "#c9d1d9",
                    "font-size": "15px",
                    "text-align": "left",
                    "margin": "2px 0",
                    "border-radius": "8px",
                    "--hover-color": "rgba(56,189,248,0.08)",
                    "font-weight": "500",
                },
                "nav-link-selected": {
                    "background": "linear-gradient(135deg, rgba(37,99,235,0.3), rgba(124,58,237,0.2))",
                    "color": "#38bdf8",
                    "font-weight": "600",
                },
            },
        )

    # Page routing
    if selected_page == "Home":
        home1.app()
    elif selected_page == "Validate Pincode":
        pin_code_correction.app()
    elif selected_page == "Handwritten Address Recognition":
        handwritten_recognition.app()
    elif selected_page == "Voice-Based Address Recognition":
        voice_address_recognition.app()
    elif selected_page == "Address Parsing":
        address_parsing.app()
    elif selected_page == "Wrong Pincode Storage":
        wrong_pincode_storage.app()
    elif selected_page == "Route Optimization":
        route_optimization.app()
    elif selected_page == "Dashboard":
        dashboard.app()


# ─── Flow Control ────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state["page"] = "home"

if st.session_state["page"] == "home":
    render_dark_theme()
    next_action = home.home_page()
    if next_action == "validate":
        st.session_state["page"] = "main"
        st.rerun()
elif st.session_state["page"] == "main":
    render_dark_theme()
    run_main_app()
