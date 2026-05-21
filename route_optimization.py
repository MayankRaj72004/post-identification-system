import math
import os

import pandas as pd
import pydeck as pdk
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


def app():
    df = load_data()

    st.markdown(
        '<div class="section-title">🗺️ Route Optimization</div>', unsafe_allow_html=True
    )
    st.markdown(
        '<div class="section-subtitle">Find nearest post offices and plan optimal delivery routes</div>',
        unsafe_allow_html=True,
    )

    # ── Input ──
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    mode = st.radio("Search mode", ["By Pincode", "By Coordinates"], horizontal=True)

    if mode == "By Pincode":
        col1, col2 = st.columns([1, 1])
        with col1:
            src_pincode = st.text_input("📍 Source Pincode", placeholder="e.g. 560001")
        with col2:
            radius_km = st.slider("🔍 Search Radius (km)", 5, 100, 25)
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            lat_input = st.number_input("📍 Latitude", value=12.9716, format="%.4f")
        with col2:
            lon_input = st.number_input("📍 Longitude", value=77.5946, format="%.4f")
        with col3:
            radius_km = st.slider("🔍 Search Radius (km)", 5, 100, 25)

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🔎  Find Nearest Post Offices", use_container_width=True):
        # Determine source coordinates
        if mode == "By Pincode":
            if not src_pincode:
                st.error("Please enter a source pincode.")
                return
            src_matches = df[df["Pincode"] == src_pincode.strip()]
            if len(src_matches) == 0:
                st.error(f"Pincode {src_pincode} not found.")
                return
            src_row = src_matches.iloc[0]
            src_lat, src_lon = src_row["Latitude"], src_row["Longitude"]
            if pd.isna(src_lat) or pd.isna(src_lon):
                st.error("Source pincode has no coordinates in the database.")
                return
            st.markdown(
                f"""
                <div class="glass-card" style="border-left:3px solid #38bdf8;">
                    <div style="font-weight:600;color:#38bdf8;">📍 Source: {src_row['OfficeName']}</div>
                    <div style="color:#94a3b8;margin-top:4px;">{src_row['District']}, {src_row['StateName']} — {src_pincode}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            src_lat, src_lon = lat_input, lon_input

        # Find nearby offices
        with st.spinner("Calculating distances..."):
            valid = df.dropna(subset=["Latitude", "Longitude"]).copy()
            valid["Distance_km"] = valid.apply(
                lambda r: haversine(src_lat, src_lon, r["Latitude"], r["Longitude"]),
                axis=1,
            )
            nearby = valid[valid["Distance_km"] <= radius_km].sort_values("Distance_km")

        if len(nearby) == 0:
            st.warning(
                f"No post offices found within {radius_km} km. Try increasing the radius."
            )
            return

        # ── Stats ──
        st.markdown("<br>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">{len(nearby)}</div>
                    <div class="metric-label">Offices Found</div>
                </div>
            """,
                unsafe_allow_html=True,
            )
        with m2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">{nearby['Distance_km'].min():.1f} km</div>
                    <div class="metric-label">Nearest</div>
                </div>
            """,
                unsafe_allow_html=True,
            )
        with m3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">{nearby['Distance_km'].max():.1f} km</div>
                    <div class="metric-label">Farthest</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Map ──
        st.markdown(
            '<div class="section-title" style="font-size:1.1rem;">🗺️ Post Offices Map</div>',
            unsafe_allow_html=True,
        )

        # Prepare Data for PyDeck
        nearby_map = nearby.copy()
        # Round the distance for better display in tooltips
        nearby_map["Distance_km"] = nearby_map["Distance_km"].round(2)

        # Format the source tooltips to match destinations
        source_data = [
            {
                "lat": src_lat,
                "lon": src_lon,
                "OfficeName": (
                    src_row["OfficeName"] if mode == "By Pincode" else "Source Location"
                ),
                "Pincode": src_pincode if mode == "By Pincode" else "N/A",
                "Distance_km": 0.0,
                "OfficeType": "Origin",
            }
        ]

        route_data = nearby_map.copy()
        route_data["src_lat"] = src_lat
        route_data["src_lon"] = src_lon

        # PyDeck layers
        source_layer = pdk.Layer(
            "ScatterplotLayer",
            data=source_data,
            get_position="[lon, lat]",
            get_color="[56, 189, 248, 200]",  # Blue-ish representing Source
            get_radius=800,
            pickable=True,
        )

        dest_layer = pdk.Layer(
            "ScatterplotLayer",
            data=nearby_map,
            get_position="[Longitude, Latitude]",
            get_color="[244, 51, 101, 200]",  # Red-ish representing Post Offices
            get_radius=400,
            pickable=True,
        )

        route_layer = pdk.Layer(
            "ArcLayer",
            data=route_data,
            get_source_position="[src_lon, src_lat]",
            get_target_position="[Longitude, Latitude]",
            get_source_color="[56, 189, 248, 150]",
            get_target_color="[244, 51, 101, 150]",
            get_width=2,
            pickable=True,
        )

        view_state = pdk.ViewState(
            latitude=src_lat,
            longitude=src_lon,
            zoom=10,
            pitch=45,
        )

        st.pydeck_chart(
            pdk.Deck(
                map_style="road",
                layers=[route_layer, source_layer, dest_layer],
                initial_view_state=view_state,
                tooltip={
                    "html": "<b>{OfficeName}</b> ({Pincode})<br/>Distance: {Distance_km} km<br/>Type: {OfficeType}",
                    "style": {
                        "color": "white",
                        "backgroundColor": "#1E1E1E",
                        "border": "1px solid #333",
                        "borderRadius": "4px",
                        "fontFamily": "Inter, sans-serif",
                    },
                },
            )
        )

        # ── Table ──
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div class="section-title" style="font-size:1.1rem;">📋 Nearby Post Offices</div>',
            unsafe_allow_html=True,
        )
        display_cols = [
            "OfficeName",
            "Pincode",
            "Distance_km",
            "OfficeType",
            "Delivery",
            "District",
            "StateName",
        ]
        display_df = nearby[display_cols].head(50).copy()
        display_df["Distance_km"] = display_df["Distance_km"].round(2)
        display_df = display_df.rename(columns={"Distance_km": "Distance (km)"})
        st.dataframe(display_df, use_container_width=True, hide_index=True)
