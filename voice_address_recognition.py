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


def app():
    df = load_data()

    st.markdown(
        '<div class="section-title">🎙️ Voice-Based Address Recognition</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">Simulate voice input — type an address as if spoken aloud, and the system will parse and validate it</div>',
        unsafe_allow_html=True,
    )

    # ── Voice Input Simulation ──
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
            <div style="
                width:56px;height:56px;border-radius:50%;
                background:linear-gradient(135deg,#ef4444,#f97316);
                display:flex;align-items:center;justify-content:center;
                font-size:24px;
                animation: pulse 2s infinite;
            ">🎙️</div>
            <div>
                <div style="font-weight:600;color:#e2e8f0;font-size:1.05rem;">Voice Input Simulation</div>
                <div style="font-size:0.8rem;color:#64748b;">Type the address as someone would speak it naturally</div>
            </div>
        </div>
        <style>
            @keyframes pulse {
                0% { box-shadow: 0 0 0 0 rgba(239,68,68,0.4); }
                70% { box-shadow: 0 0 0 15px rgba(239,68,68,0); }
                100% { box-shadow: 0 0 0 0 rgba(239,68,68,0); }
            }
        </style>
    """,
        unsafe_allow_html=True,
    )

    voice_input = st.text_area(
        "Speak your address:",
        height=100,
        placeholder='e.g. "My address is number 42, MG Road, Bangalore, Karnataka, pincode five six zero zero three four"',
        label_visibility="collapsed",
    )

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🔊  Process Voice Input", use_container_width=True):
        if not voice_input.strip():
            st.error("Please enter a voice-simulated address.")
            return

        with st.spinner("🎧 Processing voice input..."):
            import time

            time.sleep(1)

        # ── Convert spoken numbers to digits ──
        word_to_digit = {
            "zero": "0",
            "one": "1",
            "two": "2",
            "three": "3",
            "four": "4",
            "five": "5",
            "six": "6",
            "seven": "7",
            "eight": "8",
            "nine": "9",
        }
        processed = voice_input.lower().strip()
        for word, digit in word_to_digit.items():
            processed = processed.replace(word, digit)

        # Remove filler words
        fillers = [
            "my address is",
            "i live at",
            "the address is",
            "please send to",
            "deliver to",
            "pincode is",
            "pin code is",
            "pin is",
            "pincode",
            "pin code",
        ]
        for f in fillers:
            processed = processed.replace(f, "")

        processed = re.sub(r"\s+", " ", processed).strip()

        # ── Show Conversion ──
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div class="section-title" style="font-size:1.2rem;">🔄 Voice-to-Text Conversion</div>',
            unsafe_allow_html=True,
        )

        v1, v2 = st.columns(2)
        with v1:
            st.markdown(
                f"""
                <div class="glass-card">
                    <div style="color:#64748b;font-size:0.8rem;text-transform:uppercase;letter-spacing:1px;font-weight:600;">🎙️ Voice Input</div>
                    <div style="color:#e2e8f0;font-size:1rem;margin-top:8px;font-style:italic;">
                        "{voice_input}"
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )
        with v2:
            st.markdown(
                f"""
                <div class="glass-card">
                    <div style="color:#64748b;font-size:0.8rem;text-transform:uppercase;letter-spacing:1px;font-weight:600;">📝 Parsed Text</div>
                    <div style="color:#38bdf8;font-size:1rem;margin-top:8px;font-weight:500;">
                        {processed}
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        # ── Extract pincode ──
        pincode_match = re.search(r"\b(\d{6})\b", processed)
        # Also try combining consecutive digits
        if not pincode_match:
            digits_only = re.sub(r"[^0-9]", "", processed)
            if len(digits_only) >= 6:
                pincode_candidate = digits_only[-6:]
                pincode_match = re.match(r"(\d{6})", pincode_candidate)

        if pincode_match:
            pincode = (
                pincode_match.group(1)
                if hasattr(pincode_match, "group")
                else pincode_candidate
            )
            matches = df[df["Pincode"] == pincode]

            st.markdown("<br>", unsafe_allow_html=True)

            if len(matches) > 0:
                row = matches.iloc[0]
                st.markdown(
                    f"""
                    <div class="glass-card" style="border-left:3px solid #22c55e;">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div>
                                <div style="font-weight:700;color:#22c55e;font-size:1.1rem;">✅ Pincode Recognized: {pincode}</div>
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

                # Show results
                r1, r2, r3 = st.columns(3)
                with r1:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-label">Pincode</div>
                            <div class="metric-value" style="font-size:1.6rem;">{pincode}</div>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )
                with r2:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-label">District</div>
                            <div style="font-size:1rem;font-weight:600;color:#e2e8f0;margin-top:8px;">{row['District']}</div>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )
                with r3:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-label">State</div>
                            <div style="font-size:1rem;font-weight:600;color:#e2e8f0;margin-top:8px;">{row['StateName']}</div>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

                st.markdown("<br>", unsafe_allow_html=True)
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
            else:
                st.warning(
                    f"⚠️ Pincode **{pincode}** recognized but not found in the database."
                )
        else:
            st.markdown(
                """
                <div class="glass-card" style="border-left:3px solid #f59e0b;">
                    <div style="font-weight:600;color:#f59e0b;">⚠️ No pincode detected from voice</div>
                    <div style="color:#94a3b8;margin-top:4px;">
                        Try saying the pincode clearly, e.g. "five six zero zero three four" or "560034".
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )

            # Fuzzy district search
            found = []
            for d in df["District"].dropna().unique():
                if len(d) > 3 and d.lower() in processed:
                    found.append(d)
            if found:
                st.markdown(
                    f'<div class="section-title" style="font-size:1rem;margin-top:16px;">🏘️ Possible District: {found[0]}</div>',
                    unsafe_allow_html=True,
                )
                st.dataframe(
                    df[df["District"] == found[0]][
                        ["OfficeName", "Pincode", "District", "StateName"]
                    ].head(15),
                    use_container_width=True,
                    hide_index=True,
                )
