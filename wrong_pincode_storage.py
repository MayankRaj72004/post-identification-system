import pandas as pd
import streamlit as st


def app():
    st.markdown(
        '<div class="section-title">📁 Wrong Pincode Storage</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">Review all incorrect pincode entries detected during validation sessions</div>',
        unsafe_allow_html=True,
    )

    # Get wrong pincodes from session state
    wrong_list = st.session_state.get("wrong_pincodes", [])

    if len(wrong_list) == 0:
        st.markdown(
            """
            <div class="glass-card" style="text-align:center; padding:50px;">
                <div style="font-size:48px;margin-bottom:16px;">📭</div>
                <div style="font-size:1.2rem;font-weight:600;color:#e2e8f0;">No Wrong Pincodes Recorded Yet</div>
                <div style="color:#64748b;margin-top:8px;max-width:500px;margin-left:auto;margin-right:auto;">
                    Go to <strong>Validate Pincode</strong> and enter an incorrect pincode.
                    All mismatches will automatically appear here for review.
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )
        return

    # ── Summary Stats ──
    df_wrong = pd.DataFrame(wrong_list)

    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{len(df_wrong)}</div>
                <div class="metric-label">Total Errors</div>
            </div>
        """,
            unsafe_allow_html=True,
        )
    with s2:
        unique_pins = df_wrong["Entered Pincode"].nunique()
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{unique_pins}</div>
                <div class="metric-label">Unique Wrong Pincodes</div>
            </div>
        """,
            unsafe_allow_html=True,
        )
    with s3:
        unique_states = df_wrong["State"].nunique()
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{unique_states}</div>
                <div class="metric-label">States Affected</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Data Table ──
    st.markdown(
        '<div class="section-title" style="font-size:1.1rem;">📋 Error Records</div>',
        unsafe_allow_html=True,
    )

    st.dataframe(df_wrong, use_container_width=True, hide_index=True)

    # ── Error Distribution ──
    if "State" in df_wrong.columns and len(df_wrong) > 1:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div class="section-title" style="font-size:1.1rem;">📊 Errors by State</div>',
            unsafe_allow_html=True,
        )
        state_counts = df_wrong["State"].value_counts()
        st.bar_chart(state_counts)

    if "District" in df_wrong.columns and len(df_wrong) > 1:
        st.markdown(
            '<div class="section-title" style="font-size:1.1rem;">🏘️ Errors by District</div>',
            unsafe_allow_html=True,
        )
        district_counts = df_wrong["District"].value_counts()
        st.bar_chart(district_counts)

    # ── Export ──
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        csv_data = df_wrong.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥  Download CSV",
            csv_data,
            "wrong_pincodes.csv",
            "text/csv",
            use_container_width=True,
        )
    with col3:
        if st.button("🗑️  Clear All Records", use_container_width=True):
            st.session_state["wrong_pincodes"] = []
            st.rerun()
