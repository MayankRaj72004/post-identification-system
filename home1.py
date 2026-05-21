import os

import pandas as pd
import streamlit as st


@st.cache_data
def load_data():
    csv_path = os.path.join(os.path.dirname(__file__), "pincode.csv")
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    # Ensure Pincode is string
    df["Pincode"] = df["Pincode"].astype(str).str.strip()
    return df


def app():
    """Home page shown inside the sidebar-based main app."""
    df = load_data()

    st.markdown(
        '<div class="section-title">📮 Welcome to AI Postal Optimizer</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">Your intelligent assistant for postal operations across India</div>',
        unsafe_allow_html=True,
    )

    # ── Quick Stats ──
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{len(df):,}</div>
                <div class="metric-label">Post Offices</div>
            </div>
        """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{df['Pincode'].nunique():,}</div>
                <div class="metric-label">Unique Pincodes</div>
            </div>
        """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{df['StateName'].nunique()}</div>
                <div class="metric-label">States / UTs</div>
            </div>
        """,
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{df['District'].nunique():,}</div>
                <div class="metric-label">Districts</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Quick Search ──
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title" style="font-size:1.2rem;">🔎 Quick Pincode Lookup</div>',
        unsafe_allow_html=True,
    )

    search_col1, search_col2 = st.columns([1, 2])
    with search_col1:
        search_type = st.selectbox(
            "Search by",
            ["Pincode", "Office Name", "District"],
            label_visibility="collapsed",
        )
    with search_col2:
        query = st.text_input(
            "Enter search term...",
            label_visibility="collapsed",
            placeholder="Type here...",
        )

    if query:
        if search_type == "Pincode":
            results = df[df["Pincode"].str.contains(query.strip(), na=False)]
        elif search_type == "Office Name":
            results = df[
                df["OfficeName"].str.contains(query.strip(), case=False, na=False)
            ]
        else:
            results = df[
                df["District"].str.contains(query.strip(), case=False, na=False)
            ]

        if len(results) > 0:
            st.success(f"Found **{len(results):,}** matching records")
            st.dataframe(
                results[
                    [
                        "OfficeName",
                        "Pincode",
                        "District",
                        "StateName",
                        "OfficeType",
                        "Delivery",
                    ]
                ].head(50),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.warning("No results found. Try a different search term.")

    st.markdown("</div>", unsafe_allow_html=True)

    # ── How it works ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title" style="font-size:1.2rem;">⚡ How It Works</div>',
        unsafe_allow_html=True,
    )

    h1, h2, h3 = st.columns(3)
    steps = [
        ("1️⃣", "Input Address", "Enter via text, handwriting, or voice"),
        (
            "2️⃣",
            "AI Processing",
            "ML identifies nearest post office & validates pincode",
        ),
        ("3️⃣", "Get Results", "Corrected pincode with post office details & map"),
    ]
    for col, (num, title, desc) in zip([h1, h2, h3], steps):
        with col:
            st.markdown(
                f"""
                <div class="glass-card" style="text-align:center;">
                    <div style="font-size:36px;">{num}</div>
                    <div style="font-size:1rem;font-weight:700;color:#e2e8f0;margin:8px 0;">{title}</div>
                    <div style="font-size:0.85rem;color:#64748b;">{desc}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )
