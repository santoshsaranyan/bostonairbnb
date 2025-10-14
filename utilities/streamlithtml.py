html_1 = """
<style>
.bottom-right {
    position: fixed;
    bottom: 0px;
    right: 9px;
    z-index: 9999;
    text-align: center;
    font-size: 10px;
    gap: 6px;
    align-items: center;
    box-shadow: 0 0 4px rgba(0, 0, 0, 0.15);
    background-color: rgba(255, 255, 255, 0.8);
    padding: 8px 12px; /* Increased padding for more spacing */
    border-radius: 10px;
}
.bottom-right a {
    text-decoration: none; /* Remove underline */
    color: inherit;
}
</style>    
<div class="bottom-right">
    <a href="https://www.linkedin.com/in/santosh-saranyan/" target="_blank"><span> Developed by Santosh Saranyan</span></a>
</div>
"""

html_2 = """
<style>
/* Global */
.stApp {
    background-color: #fdfdfd;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1d1d1f;
}
/* Title */
.pipeline-title {
    font-size: 28px;
    font-weight: 700;
    letter-spacing: -0.5px;
    margin: 0 0 4px 0;
    color: #000;
}
.pipeline-sub {
    font-size: 15px;
    color: #6e6e73;
    margin-bottom: 24px;
}
/* Progress bar */
.progress-container {
    height: 6px;
    border-radius: 4px;
    background: #e5e5ea;
    overflow: hidden;
    margin-bottom: 20px;
}
.progress-bar {
    height: 100%;
    background: linear-gradient(90deg, #007aff, #34c759);
    transition: width 0.4s ease;
}
/* Expander tweaks */
[data-testid="stExpander"] {
    border-radius: 14px;
    border: 1px solid #e5e5ea;
    background: #fff;
    box-shadow: 0 6px 16px rgba(0,0,0,0.06);
    margin-bottom: 16px;
}
[data-testid="stExpander"] .streamlit-expanderHeader {
    font-size: 16px;
    font-weight: 600;
    color: #1d1d1f;
}
/* Buttons */
button[kind="primary"] {
    background: linear-gradient(135deg, #007aff, #34c759) !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.2rem !important;
}
</style>
"""

html_3 = """
<style>
.deck-tooltip {
    max-width: 300px !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
    font-size: 13px !important;
    line-height: 1.5 !important;
    background: white !important;
    color: black !important;
    border-radius: 8px !important;
}

.deck-tooltip b {
    font-size: 14px;
}
</style>
"""