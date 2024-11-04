# visualisation/css.py

import streamlit as st

# Custom CSS for mobile responsiveness
def add_custom_css():
    st.markdown("""
    <style>
    /* Make the page content wider */
    .appview-container .main .block-container {
        max-width: 100%;
        padding: 1rem;
    }
    /* Hide scrollbars on mobile and enable smooth side scrolling */
    .stDataFrame div[data-testid="stHorizontalScroll"] {
        overflow-x: scroll;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none;  /* Firefox */
    }
    .stDataFrame div[data-testid="stHorizontalScroll"]::-webkit-scrollbar {
        display: none;  /* Safari and Chrome */
    }
    /* Make tables more compact */
    .stDataFrame table {
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)