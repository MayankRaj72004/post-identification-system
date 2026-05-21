import streamlit as st


def home_page():
    """Landing page with hero section and call-to-action."""

    st.markdown(
        """
        <div style="text-align:center; padding:60px 20px 30px 20px;">
            <div style="font-size:72px; margin-bottom:10px;">📮</div>
            <h1 style="
                font-size:3.2rem;
                font-weight:800;
                background: linear-gradient(135deg, #38bdf8, #818cf8, #c084fc);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 8px;
                line-height: 1.2;
            ">AI-Powered Postal System</h1>
            <p style="
                font-size:1.2rem;
                color:#94a3b8;
                max-width:700px;
                margin:0 auto 10px auto;
                line-height:1.7;
            ">
                Smart Pincode Validation & Correction System — Enhancing postal operations
                with machine learning, geospatial analysis, and intelligent address recognition.
            </p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # ── Feature Cards ──
    st.markdown(
        '<div style="max-width:1000px; margin:0 auto;">', unsafe_allow_html=True
    )

    cols = st.columns(3)
    features = [
        (
            "🔍",
            "Pincode Validation",
            "Verify and auto-correct pincodes against 1.5 lakh+ post offices across India.",
        ),
        (
            "✍️",
            "Handwritten Recognition",
            "AI-powered recognition of handwritten addresses converted to structured data.",
        ),
        (
            "🎙️",
            "Voice Input",
            "Speak your address — our system parses and validates it in real-time.",
        ),
        (
            "📊",
            "Analytics Dashboard",
            "Visualize pincode error hotspots by region, state, and city.",
        ),
        (
            "🗺️",
            "Route Optimization",
            "Find the nearest post offices and optimal delivery routes.",
        ),
        (
            "📋",
            "Address Parsing",
            "Extract structured fields from raw address strings automatically.",
        ),
    ]

    for i, (icon, title, desc) in enumerate(features):
        col = cols[i % 3]
        with col:
            st.markdown(
                f"""
                <div class="glass-card" style="text-align:center; min-height:200px;">
                    <div style="font-size:40px; margin-bottom:10px;">{icon}</div>
                    <div style="font-size:1.1rem; font-weight:700; color:#e2e8f0; margin-bottom:8px;">
                        {title}
                    </div>
                    <div style="font-size:0.9rem; color:#64748b; line-height:1.6;">
                        {desc}
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Stats Bar ──
    st.markdown("<br>", unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    stats = [
        ("1,55,000+", "Post Offices"),
        ("19,000+", "Unique Pincodes"),
        ("36", "States & UTs"),
        ("99.2%", "Accuracy"),
    ]
    for col, (val, label) in zip([s1, s2, s3, s4], stats):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">{val}</div>
                    <div class="metric-label">{label}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

    # ── CTA Button ──
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("🚀  Launch Application", use_container_width=True):
            return "validate"

    st.markdown(
        """
        <div style="text-align:center; margin-top:40px; padding-bottom:30px;">
            <p style="color:#475569; font-size:0.8rem;">
                Built with ❤️ using Streamlit • Data from India Post
            </p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    return None
