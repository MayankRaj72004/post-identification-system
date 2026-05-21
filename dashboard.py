import os

import pandas as pd
import streamlit as st


@st.cache_data
def load_data():
    csv_path = os.path.join(os.path.dirname(__file__), "pincode.csv")
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    df["Pincode"] = df["Pincode"].astype(str).str.strip()
    df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
    df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
    return df


def app():
    df = load_data()

    st.markdown(
        '<div class="section-title">📊 Postal Analytics Dashboard</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">Comprehensive view of India Post office distribution, coverage, and insights</div>',
        unsafe_allow_html=True,
    )

    # ══════════════════════════════════════════════════════════════════════════
    # TOP METRICS
    # ══════════════════════════════════════════════════════════════════════════
    m1, m2, m3, m4, m5 = st.columns(5)
    metrics = [
        (f"{len(df):,}", "Total Offices"),
        (f"{df['Pincode'].nunique():,}", "Unique Pincodes"),
        (f"{df['StateName'].nunique()}", "States / UTs"),
        (f"{df['District'].nunique():,}", "Districts"),
        (f"{df['CircleName'].nunique()}", "Postal Circles"),
    ]
    for col, (val, label) in zip([m1, m2, m3, m4, m5], metrics):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value" style="font-size:1.6rem;">{val}</div>
                    <div class="metric-label">{label}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TABS
    # ══════════════════════════════════════════════════════════════════════════
    tab1, tab2, tab3, tab4 = st.tabs(
        ["🏛️ State Analysis", "🏘️ District View", "📮 Office Types", "🗺️ Map View"]
    )

    # ── Tab 1: State Analysis ──
    with tab1:
        st.markdown(
            '<div class="section-title" style="font-size:1.1rem;">📊 Post Offices by State</div>',
            unsafe_allow_html=True,
        )

        state_counts = df["StateName"].value_counts().head(20)
        st.bar_chart(state_counts, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Pincodes per state
        st.markdown(
            '<div class="section-title" style="font-size:1.1rem;">🔢 Unique Pincodes by State (Top 20)</div>',
            unsafe_allow_html=True,
        )
        pin_per_state = (
            df.groupby("StateName")["Pincode"]
            .nunique()
            .sort_values(ascending=False)
            .head(20)
        )
        st.bar_chart(pin_per_state, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # State details table
        st.markdown(
            '<div class="section-title" style="font-size:1.1rem;">📋 State-wise Summary</div>',
            unsafe_allow_html=True,
        )
        state_summary = (
            df.groupby("StateName")
            .agg(
                Total_Offices=("OfficeName", "count"),
                Unique_Pincodes=("Pincode", "nunique"),
                Districts=("District", "nunique"),
                Delivery_Offices=("Delivery", lambda x: (x == "Delivery").sum()),
            )
            .sort_values("Total_Offices", ascending=False)
            .reset_index()
        )
        state_summary.columns = [
            "State",
            "Total Offices",
            "Unique Pincodes",
            "Districts",
            "Delivery Offices",
        ]
        st.dataframe(state_summary, use_container_width=True, hide_index=True)

    # ── Tab 2: District View ──
    with tab2:
        selected_state = st.selectbox(
            "Select a State",
            sorted(df["StateName"].dropna().unique()),
            index=None,
            placeholder="Choose a state...",
        )

        if selected_state:
            state_df = df[df["StateName"] == selected_state]

            d1, d2, d3 = st.columns(3)
            with d1:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-value" style="font-size:1.5rem;">{len(state_df):,}</div>
                        <div class="metric-label">Offices in {selected_state[:15]}</div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
            with d2:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-value" style="font-size:1.5rem;">{state_df['District'].nunique()}</div>
                        <div class="metric-label">Districts</div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
            with d3:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-value" style="font-size:1.5rem;">{state_df['Pincode'].nunique():,}</div>
                        <div class="metric-label">Pincodes</div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown(
                f'<div class="section-title" style="font-size:1.1rem;">📊 Offices by District in {selected_state}</div>',
                unsafe_allow_html=True,
            )
            dist_counts = state_df["District"].value_counts().head(20)
            st.bar_chart(dist_counts, use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # District detail table
            dist_summary = (
                state_df.groupby("District")
                .agg(
                    Offices=("OfficeName", "count"),
                    Pincodes=("Pincode", "nunique"),
                )
                .sort_values("Offices", ascending=False)
                .reset_index()
            )
            st.dataframe(dist_summary, use_container_width=True, hide_index=True)

    # ── Tab 3: Office Types ──
    with tab3:
        st.markdown(
            '<div class="section-title" style="font-size:1.1rem;">🏤 Office Type Distribution</div>',
            unsafe_allow_html=True,
        )

        type_counts = df["OfficeType"].value_counts()

        t1, t2 = st.columns([1, 1])
        with t1:
            for otype, count in type_counts.items():
                pct = count / len(df) * 100
                label_map = {
                    "BO": "Branch Office",
                    "SO": "Sub Office",
                    "HO": "Head Office",
                    "GPO": "General Post Office",
                }
                full_name = label_map.get(otype, otype)
                st.markdown(
                    f"""
                    <div class="glass-card" style="padding:16px;margin-bottom:10px;">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div>
                                <div style="font-weight:600;color:#e2e8f0;">{full_name} ({otype})</div>
                                <div style="color:#64748b;font-size:0.85rem;">{count:,} offices</div>
                            </div>
                            <div class="metric-value" style="font-size:1.2rem;">{pct:.1f}%</div>
                        </div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

        with t2:
            st.bar_chart(type_counts, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Delivery vs Non-Delivery
        st.markdown(
            '<div class="section-title" style="font-size:1.1rem;">📦 Delivery Status</div>',
            unsafe_allow_html=True,
        )
        del_counts = df["Delivery"].value_counts()
        dc1, dc2 = st.columns(2)
        for col, (status, count) in zip([dc1, dc2], del_counts.items()):
            with col:
                color = "#22c55e" if status == "Delivery" else "#f59e0b"
                st.markdown(
                    f"""
                    <div class="metric-card" style="border:1px solid {color}33;">
                        <div class="metric-value" style="font-size:1.6rem;background:none;-webkit-text-fill-color:{color};">{count:,}</div>
                        <div class="metric-label">{status}</div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

    # ── Tab 4: Map View ──
    with tab4:
        st.markdown(
            '<div class="section-title" style="font-size:1.1rem;">🗺️ Post Office Locations</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="section-subtitle">Showing a sample of post offices across India</div>',
            unsafe_allow_html=True,
        )

        map_state = st.selectbox(
            "Filter by State (optional)",
            ["All India"] + sorted(df["StateName"].dropna().unique().tolist()),
            key="map_state",
        )

        if map_state == "All India":
            map_df = df.dropna(subset=["Latitude", "Longitude"]).sample(
                min(3000, len(df)), random_state=42
            )
        else:
            map_df = df[(df["StateName"] == map_state)].dropna(
                subset=["Latitude", "Longitude"]
            )
            if len(map_df) > 3000:
                map_df = map_df.sample(3000, random_state=42)

        map_display = map_df[["Latitude", "Longitude"]].rename(
            columns={"Latitude": "lat", "Longitude": "lon"}
        )
        st.map(map_display, zoom=4 if map_state == "All India" else 6)

        st.info(f"Showing **{len(map_display):,}** post office locations on the map.")
