import os
import re

import pandas as pd
import streamlit as st


@st.cache_data
def load_data():
    csv_path = os.path.join(os.path.dirname(__file__), "pincode.csv")
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    df["Pincode"] = df["Pincode"].astype(str).str.strip()
    return df


def simulate_ocr(text):
    """Simulate OCR-like processing on handwritten text input."""
    cleaned = text.strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def app():
    df = load_data()

    st.markdown(
        '<div class="section-title">✍️ Typed Address Recognition</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">Simulate handwritten address input — type as if writing by hand, and the AI will parse and validate it</div>',
        unsafe_allow_html=True,
    )

    # ── Input Section ──
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">
            <span style="font-size:28px;">📝</span>
            <div>
                <div style="font-weight:600;color:#e2e8f0;">Handwriting Input Simulation</div>
                <div style="font-size:0.8rem;color:#64748b;">Type the address as it might appear in handwriting (messy, abbreviated, etc.)</div>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    handwritten_input = st.text_area(
        "Write the address here:",
        height=130,
        placeholder="e.g. Raju Sharma, 12 main rd, krmngla, bnglore, karntaka 560034",
        label_visibility="collapsed",
    )

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🔎  Recognize & Validate", use_container_width=True):
        if not handwritten_input.strip():
            st.error("Please enter a handwritten address.")
            return

        processed = simulate_ocr(handwritten_input)

        # ── OCR Processing Animation ──
        st.markdown("<br>", unsafe_allow_html=True)
        with st.spinner("🤖 Processing handwritten input..."):
            import time

            time.sleep(1)

        st.markdown(
            '<div class="section-title" style="font-size:1.2rem;">🔍 Recognition Result</div>',
            unsafe_allow_html=True,
        )

        # Show original vs processed
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                f"""
                <div class="glass-card">
                    <div style="color:#64748b;font-size:0.8rem;text-transform:uppercase;letter-spacing:1px;font-weight:600;">📥 Raw Input</div>
                    <div style="color:#e2e8f0;font-size:1rem;margin-top:8px;font-style:italic;font-family:cursive;">
                        {handwritten_input}
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"""
                <div class="glass-card">
                    <div style="color:#64748b;font-size:0.8rem;text-transform:uppercase;letter-spacing:1px;font-weight:600;">📤 Processed Text</div>
                    <div style="color:#38bdf8;font-size:1rem;margin-top:8px;font-weight:500;">
                        {processed}
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        # ── Extract pincode ──
        pincode_match = re.search(r"\b(\d{6})\b", processed)
        if pincode_match:
            pincode = pincode_match.group(1)
            matches = df[df["Pincode"] == pincode]

            st.markdown("<br>", unsafe_allow_html=True)

            if len(matches) > 0:
                row = matches.iloc[0]
                st.markdown(
                    f"""
                    <div class="glass-card" style="border-left:3px solid #22c55e;">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div>
                                <div style="font-weight:700;color:#22c55e;font-size:1.1rem;">✅ Pincode Identified: {pincode}</div>
                                <div style="color:#94a3b8;margin-top:4px;">
                                    {row['OfficeName']} • {row['District']} • {row['StateName']}
                                </div>
                            </div>
                            <span class="status-correct">VALID</span>
                        </div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    '<div class="section-title" style="font-size:1rem;margin-top:20px;">🏤 Matching Post Offices</div>',
                    unsafe_allow_html=True,
                )
                st.dataframe(
                    matches[
                        [
                            "OfficeName",
                            "Pincode",
                            "District",
                            "StateName",
                            "OfficeType",
                            "Delivery",
                        ]
                    ].head(15),
                    use_container_width=True,
                    hide_index=True,
                )

                # Map
                map_df = matches[["Latitude", "Longitude"]].dropna()
                map_df.columns = ["lat", "lon"]
                map_df = map_df[map_df["lat"].notna() & map_df["lon"].notna()]
                if len(map_df) > 0:
                    st.map(map_df, zoom=11)
            else:
                st.warning(
                    f"⚠️ Pincode **{pincode}** was extracted but not found in the database."
                )
        else:
            # Try matching by district/state keywords
            st.markdown(
                """
                <div class="glass-card" style="border-left:3px solid #f59e0b;">
                    <div style="font-weight:600;color:#f59e0b;">⚠️ No pincode detected in the text</div>
                    <div style="color:#94a3b8;margin-top:4px;">
                        Try including a 6-digit pincode in your handwritten input for better results.
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )

            # Attempt fuzzy district matching
            found_districts = []
            for d in df["District"].dropna().unique():
                if len(d) > 3 and d.lower() in processed.lower():
                    found_districts.append(d)

            if found_districts:
                st.markdown(
                    f'<div class="section-title" style="font-size:1rem;margin-top:16px;">🏘️ Detected District: {found_districts[0]}</div>',
                    unsafe_allow_html=True,
                )
                district_matches = df[df["District"] == found_districts[0]]
                st.dataframe(
                    district_matches[
                        ["OfficeName", "Pincode", "District", "StateName"]
                    ].head(15),
                    use_container_width=True,
                    hide_index=True,
                )
