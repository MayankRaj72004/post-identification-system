import math
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


def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two lat/lon points."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def find_nearest_office(df, district, state):
    """Find the best matching post office for given district/state."""
    matches = df[
        (df["District"].str.upper() == district.upper())
        & (df["StateName"].str.upper() == state.upper())
    ]
    if len(matches) == 0:
        matches = df[df["District"].str.upper() == district.upper()]
    if len(matches) == 0:
        matches = df[df["District"].str.contains(district, case=False, na=False)]
    return matches


def app():
    df = load_data()

    st.markdown(
        '<div class="section-title">✅ Pincode Validation & Correction</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">Enter an address to validate the pincode and auto-correct it if needed</div>',
        unsafe_allow_html=True,
    )

    # ── Input Form ──
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        state = st.selectbox(
            "🏛️ State",
            sorted(df["StateName"].dropna().unique()),
            index=None,
            placeholder="Select a state...",
        )
    with col2:
        if state:
            districts = sorted(
                df[df["StateName"] == state]["District"].dropna().unique()
            )
        else:
            districts = sorted(df["District"].dropna().unique())
        district = st.selectbox(
            "🏘️ District", districts, index=None, placeholder="Select a district..."
        )

    col3, col4 = st.columns(2)
    with col3:
        if district:
            offices = sorted(
                df[df["District"] == district]["OfficeName"].dropna().unique()
            )
        else:
            offices = []
        office = st.selectbox("🏤 Post Office (optional)", [""] + offices, index=0)
    with col4:
        input_pincode = st.text_input(
            "📮 Enter Pincode to Validate", placeholder="e.g. 560001"
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Validate Button ──
    if st.button("🔍  Validate Pincode", use_container_width=True):
        if not district:
            st.error("Please select at least a district to validate.")
            return

        if office and office != "":
            matches = df[df["OfficeName"] == office]
        else:
            matches = find_nearest_office(df, district, state if state else "")

        if len(matches) == 0:
            st.error("❌ No matching post office found for the given location.")
            return

        correct_row = matches.iloc[0]
        correct_pincode = str(correct_row["Pincode"])

        # ── Results ──
        st.markdown("<br>", unsafe_allow_html=True)

        if input_pincode.strip() == "":
            st.info("ℹ️ No pincode entered. Showing the correct pincode for this area.")
            status_html = '<span class="status-corrected">📌 SUGGESTED</span>'
        elif input_pincode.strip() == correct_pincode:
            status_html = '<span class="status-correct">✅ CORRECT</span>'
            # Store in session state for tracking
        else:
            status_html = '<span class="status-incorrect">❌ INCORRECT</span>'
            # Store wrong pincode
            if "wrong_pincodes" not in st.session_state:
                st.session_state["wrong_pincodes"] = []
            st.session_state["wrong_pincodes"].append(
                {
                    "Entered Pincode": input_pincode.strip(),
                    "Correct Pincode": correct_pincode,
                    "Office": correct_row["OfficeName"],
                    "District": correct_row["District"],
                    "State": correct_row["StateName"],
                }
            )

        st.markdown(
            f"""
            <div class="glass-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                    <div class="section-title" style="font-size:1.2rem; margin:0;">📋 Validation Result</div>
                    {status_html}
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )

        r1, r2, r3 = st.columns(3)
        with r1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Correct Pincode</div>
                    <div class="metric-value" style="font-size:1.8rem;">{correct_pincode}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )
        with r2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Post Office</div>
                    <div style="font-size:1.1rem;font-weight:700;color:#e2e8f0;margin-top:8px;">{correct_row['OfficeName']}</div>
                    <div style="font-size:0.8rem;color:#64748b;margin-top:4px;">{correct_row.get('OfficeType', 'N/A')}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )
        with r3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Location</div>
                    <div style="font-size:1rem;font-weight:600;color:#e2e8f0;margin-top:8px;">{correct_row['District']}</div>
                    <div style="font-size:0.85rem;color:#64748b;margin-top:4px;">{correct_row['StateName']}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        # ── Show on Map ──
        lat = correct_row.get("Latitude")
        lon = correct_row.get("Longitude")
        if pd.notna(lat) and pd.notna(lon):
            st.markdown("<br>", unsafe_allow_html=True)
            map_df = (
                matches[["Latitude", "Longitude"]]
                .dropna()
                .rename(columns={"Latitude": "lat", "Longitude": "lon"})
            )
            st.map(map_df, zoom=10)

        # ── Nearby Offices ──
        if input_pincode.strip() != correct_pincode and input_pincode.strip() != "":
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="glass-card" style="border-left: 3px solid #38bdf8;">
                    <div style="font-size:1rem;font-weight:600;color:#38bdf8;">💡 Correction Applied</div>
                    <div style="color:#94a3b8;margin-top:6px;">
                        Your entered pincode <strong style="color:#ef4444;">{input_pincode.strip()}</strong>
                        has been corrected to <strong style="color:#22c55e;">{correct_pincode}</strong>
                        for <strong style="color:#e2e8f0;">{correct_row['OfficeName']}</strong>, {correct_row['District']}.
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        # Show nearby offices table
        if len(matches) > 1:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<div class="section-title" style="font-size:1.1rem;">🏤 Other Post Offices in Area</div>',
                unsafe_allow_html=True,
            )
            st.dataframe(
                matches[
                    [
                        "OfficeName",
                        "Pincode",
                        "OfficeType",
                        "Delivery",
                        "District",
                        "StateName",
                    ]
                ].head(20),
                use_container_width=True,
                hide_index=True,
            )
