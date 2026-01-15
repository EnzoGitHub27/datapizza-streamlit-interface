# ui/styles.py
# Datapizza v1.5.0 - Stili CSS (Gemini-like & Frontier UI)
# ============================================================================

MAIN_CSS = """
<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Chat Buckets */
.user-bubble {
    background-color: #0084ff !important; /* Messenger-like Blue */
    padding: 12px 16px !important;
    border-radius: 18px 18px 4px 18px !important;
    margin-bottom: 8px !important;
    color: #ffffff !important;
    max-width: fit-content !important;
    margin-left: auto !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    font-size: 15px;
    line-height: 1.5;
}

.assistant-bubble {
    background-color: #f0f2f5 !important;
    padding: 12px 16px !important;
    border-radius: 18px 18px 18px 4px !important;
    margin-bottom: 8px !important;
    color: #050505 !important;
    max-width: fit-content !important;
    margin-right: auto !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    font-size: 15px;
    line-height: 1.5;
    border: none !important;
}

@media (prefers-color-scheme: dark) {
    .user-bubble { 
        background-color: #0084ff !important; 
        color: #ffffff !important; 
        box-shadow: none;
    }
    .assistant-bubble { 
        background-color: #303030 !important;
        color: #e4e6eb !important; 
        box-shadow: none;
    }
}

/* Top Stats Bar used in Top Bar */
.stats-container {
    display: flex;
    gap: 1.5rem;
    align-items: center;
}

.stat-item {
    text-align: center;
    border-right: 1px solid rgba(255, 255, 255, 0.1);
    padding-right: 1.5rem;
}

.stat-item:last-child {
    border-right: none;
    padding-right: 0;
}

.stat-value {
    font-size: 1rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}

.stat-label {
    font-size: 0.7rem;
    opacity: 0.6;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Themes per Local (Green) vs Cloud (Red) */
/* Applicati dinamicamente via st.markdown */

/* Sidebar Width Constraint (20% of viewport) */
[data-testid="stSidebar"] {
    width: 20vw !important;
    min-width: 250px;
    max-width: 350px;
}

[data-testid="stSidebar"] > div:first-child {
    width: 20vw !important;
    min-width: 250px;
    max-width: 350px;
}

/* Custom scrollbar for sidebar */
[data-testid="stSidebar"]::-webkit-scrollbar {
    width: 8px;
}

[data-testid="stSidebar"]::-webkit-scrollbar-track {
    background: transparent;
}

[data-testid="stSidebar"]::-webkit-scrollbar-thumb {
    background: rgba(128, 128, 128, 0.3);
    border-radius: 4px;
}

[data-testid="stSidebar"]::-webkit-scrollbar-thumb:hover {
    background: rgba(128, 128, 128, 0.5);
}

</style>
"""

# Toggle Switch CSS (Segmented Control Style)
TOGGLE_SWITCH_CSS = """
<style>
/* Target the Radio Group in Sidebar */
[data-testid="stSidebar"] [data-testid="stRadio"] > div[role="radiogroup"] {
    background-color: rgba(128, 128, 128, 0.1);
    padding: 4px;
    border-radius: 8px;
    display: flex;
    justify-content: space-between;
    gap: 0;
}

/* Hide the default radio circles */
[data-testid="stSidebar"] [data-testid="stRadio"] input[type="radio"] {
    display: none;
}

/* Style the labels (the clickable area) */
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    flex: 1;
    text-align: center;
    padding: 6px 1px;
    border-radius: 6px;
    border: none;
    margin: 0;
    transition: all 0.2s ease;
    cursor: pointer;
    font-weight: 500;
    font-size: 0.9rem;
    color: inherit;
    display: flex;
    justify-content: center;
    align-items: center;
}

/* Hover state for labels */
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background-color: rgba(128, 128, 128, 0.05);
}

/* SELECTED State - This is tricky in pure CSS without :has() or structure control.
   Streamlit adds data-checked="true" to the div wrapping the input, or we rely on the specific DOM structure.
   
   However, Streamlit 1.28+ usually renders structure like:
   div[role="radiogroup"]
     label
       div[data-testid="stMarkdownContainer"]
         p
       div
         input
         div (the circle)
         
   Wait, Streamlit's radio styling is hard to override purely due to the DOM structure varying.
   
   Newer Strategy: We can use the fact that the checked input is a sibling or child.
   Actually, Streamlit applies a class or attribute to the selected LABEL or its container.
   
   Let's try a robust approach:
   We will style the *content* inside the label.
*/

/* HACK: Highlight the selected one. 
   Streamlit's rendered HTML for radio puts the input inside the label or adjacent.
   If checked, the label text usually gets bolded by Streamlit or the circle gets color.
   
   Since we can't reliably select the PARENT label based on the child input state in old CSS without :has(),
   we might need to rely on the background highlighting that Streamlit applies? 
   No, Streamlit only colors the circle.
   
   Fortunately, modern browsers support :has().
   And for a Mac user in 2026, :has() is safe.
*/

[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background-color: var(--background-color, #ffffff);
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    font-weight: 600;
}

@media (prefers-color-scheme: dark) {
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        background-color: #262730; /* Streamlit dark bg */
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }
}
</style>
"""

# Theme: LOCAL (Green)
THEME_LOCAL = """
<style>
/* Sidebar Accent */
[data-testid="stSidebar"] {
    border-right: 3px solid #4CAF50 !important;
}
/* Main Header Accent */
.stApp header {
    background: linear-gradient(90deg, transparent 0%, rgba(76, 175, 80, 0.1) 100%);
}
/* Chat Input Focus */
.stTextInput textarea:focus, .stTextArea textarea:focus {
    border-color: #4CAF50 !important;
    box-shadow: 0 0 0 1px #4CAF50 !important;
}
/* Primary Buttons */
button[kind="primary"] {
    background-color: #4CAF50 !important;
    border-color: #4CAF50 !important;
}
/* Status Indicator */
.connection-status {
    color: #4CAF50;
    font-weight: bold;
    border: 1px solid #4CAF50;
    padding: 2px 10px;
    border-radius: 20px;
    background: rgba(76, 175, 80, 0.1);
    font-size: 0.8rem;
}
</style>
"""

# Theme: CLOUD (Red)
THEME_CLOUD = """
<style>
/* Sidebar Accent */
[data-testid="stSidebar"] {
    border-right: 3px solid #ff6b6b !important;
}
/* Main Header Accent */
.stApp header {
    background: linear-gradient(90deg, transparent 0%, rgba(255, 107, 107, 0.1) 100%);
}
/* Chat Input Focus */
.stTextInput textarea:focus, .stTextArea textarea:focus {
    border-color: #ff6b6b !important;
    box-shadow: 0 0 0 1px #ff6b6b !important;
}
/* Primary Buttons */
button[kind="primary"] {
    background-color: #ff6b6b !important;
    border-color: #ff6b6b !important;
}
/* Status Indicator */
.connection-status {
    color: #ff6b6b;
    font-weight: bold;
    border: 1px solid #ff6b6b;
    padding: 2px 10px;
    border-radius: 20px;
    background: rgba(255, 107, 107, 0.1);
    font-size: 0.8rem;
}
</style>
"""


# Fixed Input Container (Chat Input)
FIXED_INPUT_CSS = """
<style>
div[data-testid="stVerticalBlockBorderWrapper"]:has(span#chat-input-anchor) {
    position: fixed;
    bottom: 0;
    left: 20vw;
    width: 80vw;
    z-index: 999;
    background-color: var(--secondary-background-color, #ffffff);
    border-top: 1px solid rgba(128, 128, 128, 0.15);
    padding: 1.5rem 2rem;
    box-shadow: 0 -4px 20px rgba(0,0,0,0.08);
}

@media (prefers-color-scheme: dark) {
    div[data-testid="stVerticalBlockBorderWrapper"]:has(span#chat-input-anchor) {
        background-color: var(--secondary-background-color, #0e0e0e);
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
}

@media (max-width: 1200px) {
    div[data-testid="stVerticalBlockBorderWrapper"]:has(span#chat-input-anchor) {
        left: 0;
        width: 100%;
    }
}
</style>
"""

# Chat Column (80% width)
CHAT_COLUMN_CSS = """
<style>
/* Chat column container */
div[data-testid="stColumn"]:has(span#chat-column-anchor) {
    width: 80vw !important;
    max-width: 80vw !important;
    min-width: 400px;
    margin-left: 0;
    padding: 1rem 10%; /* Center chat content with some padding */
}

/* Compensate for Top Bar */
.main .block-container {
    padding-top: 5rem !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    max-width: none !important;
}

/* Ensure proper spacing and scrolling */
main > div[data-testid="stVerticalBlock"] {
    gap: 0 !important;
}
</style>
"""

# Fixed Top Bar (spans across chat and config, 80% of viewport)
FIXED_TOP_BAR_CSS = """
<style>
div[data-testid="stVerticalBlockBorderWrapper"]:has(span#top-bar-anchor) {
    position: fixed;
    top: 0;
    left: 20vw; /* After sidebar */
    right: 0;
    width: 80vw;
    height: 4.5rem;
    z-index: 1000;
    background-color: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 2px solid rgba(128, 128, 128, 0.1);
    display: flex;
    align-items: center;
    padding: 0 2.5rem;
    box-shadow: 0 2px 15px rgba(0,0,0,0.04);
}

@media (prefers-color-scheme: dark) {
    div[data-testid="stVerticalBlockBorderWrapper"]:has(span#top-bar-anchor) {
        background-color: rgba(14, 14, 14, 0.95);
        border-bottom: 2px solid rgba(255, 255, 255, 0.08);
    }
}

@media (max-width: 1200px) {
    div[data-testid="stVerticalBlockBorderWrapper"]:has(span#top-bar-anchor) {
        left: 0;
        width: 100vw;
    }
}

/* Ensure content inside doesn't wrap weirdly */
div[data-testid="stVerticalBlockBorderWrapper"]:has(span#top-bar-anchor) > div {
    width: 100%;
}
</style>
"""



