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


def parse_address(raw_address, df):
    """Parse raw address string and try to extract structured fields."""
    text = raw_address.strip()
    result = {
        "Raw Address": raw_address,
        "Pincode": "",
        "State": "",
        "District": "",
        "Post Office": "",
        "Remaining": text,
    }

    # Extract pincode (6 digit number)
    pincode_match = re.search(r"\b(\d{6})\b", text)
    if pincode_match:
        result["Pincode"] = pincode_match.group(1)
        text = text.replace(pincode_match.group(0), "").strip()

    # Try to match state
    states = df["StateName"].dropna().unique()
    for s in states:
        if s.lower() in text.lower():
            result["State"] = s
            text = re.sub(re.escape(s), "", text, flags=re.IGNORECASE).strip()
            break

    # Try to match district
    districts = df["District"].dropna().unique()
    for d in districts:
        if d.lower() in text.lower():
            result["District"] = d
            text = re.sub(re.escape(d), "", text, flags=re.IGNORECASE).strip()
            break

    # Try to match office
    if result["District"]:
        offices = (
            df[df["District"].str.upper() == result["District"].upper()]["OfficeName"]
            .dropna()
            .unique()
        )
        for o in offices:
            if o.lower() in text.lower():
                result["Post Office"] = o
                text = re.sub(re.escape(o), "", text, flags=re.IGNORECASE).strip()
                break

    # Clean remaining
    result["Remaining"] = re.sub(r"[,\s]+", " ", text).strip()

    return result


def app():
    df = load_data()

    st.markdown(
        '<div class="section-title">📋 Address Parsing</div>', unsafe_allow_html=True
    )
    st.markdown(
        '<div class="section-subtitle">Extract structured data from raw address strings automatically</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    raw_address = st.text_area(
        "📝 Enter raw address",
        height=120,
        placeholder="e.g. Ramesh Kumar, Plot 42, MG Road, Koramangala, BANGALORE, KARNATAKA 560034",
    )

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🔍  Parse Address", use_container_width=True):
        if not raw_address.strip():
            st.error("Please enter an address to parse.")
            return

        result = parse_address(raw_address, df)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div class="section-title" style="font-size:1.2rem;">📊 Parsed Result</div>',
            unsafe_allow_html=True,
        )

        p1, p2, p3 = st.columns(3)
        with p1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Pincode</div>
                    <div class="metric-value" style="font-size:1.6rem;">{result['Pincode'] or '—'}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )
        with p2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">State</div>
                    <div style="font-size:1.1rem;font-weight:700;color:#e2e8f0;margin-top:8px;">{result['State'] or '—'}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )
        with p3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">District</div>
                    <div style="font-size:1.1rem;font-weight:700;color:#e2e8f0;margin-top:8px;">{result['District'] or '—'}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        p4, p5 = st.columns(2)
        with p4:
            st.markdown(
                f"""
                <div class="glass-card">
                    <div style="color:#64748b;font-size:0.8rem;text-transform:uppercase;letter-spacing:1px;font-weight:600;">Post Office</div>
                    <div style="color:#e2e8f0;font-size:1rem;margin-top:6px;">{result['Post Office'] or 'Not identified'}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )
        with p5:
            st.markdown(
                f"""
                <div class="glass-card">
                    <div style="color:#64748b;font-size:0.8rem;text-transform:uppercase;letter-spacing:1px;font-weight:600;">Remaining / Street Address</div>
                    <div style="color:#e2e8f0;font-size:1rem;margin-top:6px;">{result['Remaining'] or '—'}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        # If pincode was found, show matching post offices
        if result["Pincode"]:
            pin_matches = df[df["Pincode"] == result["Pincode"]]
            if len(pin_matches) > 0:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(
                    f'<div class="section-title" style="font-size:1.1rem;">🏤 Post Offices for Pincode {result["Pincode"]}</div>',
                    unsafe_allow_html=True,
                )
                st.dataframe(
                    pin_matches[
                        ["OfficeName", "Pincode", "District", "StateName", "OfficeType"]
                    ].head(20),
                    use_container_width=True,
                    hide_index=True,
                )

        # JSON output
        with st.expander("📄 View as JSON"):
            st.json(result)
