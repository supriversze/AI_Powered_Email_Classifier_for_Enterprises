import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import os
import requests

# ---------- Backend API Config ----------
# Update this URL to match the backend team's deployed server
API_URL = "http://localhost:8000/classify"

# ---------- Config ----------
st.set_page_config(
    page_title="AI Email Classifier",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded",
)

if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# ---------- Custom Styles ----------
def inject_custom_css():
    if st.session_state.theme == 'dark':
        bg = "#0d1117"
        text = "#c9d1d9"
        sidebar_bg = "#161b22"
        sidebar_border = "#30363d"
        card_bg = "#1e2532"
        card_border = "#30363d"
        card_hover_shadow = "rgba(0,0,0,0.3)"
        title_color = "#58a6ff"
        label_color = "#8b949e"
        sender_color = "#e6edf3"
        time_color = "#8b949e"
        tag_bg = "#30363d"
    else:
        bg = "#f3f4f6"
        text = "#1f2937"
        sidebar_bg = "#ffffff"
        sidebar_border = "#e5e7eb"
        card_bg = "#ffffff"
        card_border = "#e5e7eb"
        card_hover_shadow = "rgba(0,0,0,0.05)"
        title_color = "#3b82f6"
        label_color = "#6b7280"
        sender_color = "#111827"
        time_color = "#6b7280"
        tag_bg = "#e5e7eb"

    css = f"""
    <style>
        /* Global App Background */
        .stApp {{
            background-color: {bg} !important; 
        }}
        
        /* Force text colors to override config.toml */
        .stApp, .stApp p, .stApp span, .stApp div[data-testid="stMarkdownContainer"] p, 
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, 
        [data-testid="stText"], [data-testid="stMetricValue"], [data-testid="stMetricLabel"],
        .stRadio label, .stCheckbox label, div[data-testid="stSelectbox"] label.st-emotion-cache-1j8985c {{
            color: {text} !important;
        }}
        
        /* Sidebar Styles */
        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg} !important;
            border-right: 1px solid {sidebar_border} !important;
        }}
        .css-1544g2n {{
            padding: 2rem 1rem;
        }}
        
        /* App Title */
        .app-title {{
             font-size: 1.5rem;
             font-weight: 700;
             color: {title_color};
             display: flex;
             align-items: center;
             gap: 10px;
             margin-bottom: 2rem;
        }}
        .app-title svg {{
            width: 24px;
            height: 24px;
            fill: currentColor;
        }}

        /* Section Label */
        .section-label {{
            color: {label_color};
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }}
        
        /* Main Content Background */
        [data-testid="stMain"] {{
            background-color: {bg} !important;
        }}

        /* Email Card Styles */
        div.email-card {{
            background-color: {card_bg};
            border: 1px solid {card_border};
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            transition: transform 0.1s ease-in-out, box-shadow 0.1s ease-in-out;
        }}
        div.email-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px {card_hover_shadow};
        }}
        .email-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}
        .email-sender {{
            font-weight: 600;
            color: {sender_color};
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .unread-dot {{
            width: 8px;
            height: 8px;
            background-color: #3b82f6;
            border-radius: 50%;
            display: inline-block;
        }}
        .email-time {{
            color: {time_color};
            font-size: 0.85rem;
        }}
        .email-subject {{
            font-weight: 700;
            font-size: 1.1rem;
            color: {sender_color};
            margin-bottom: 8px;
        }}
        .email-snippet {{
            color: {label_color};
            font-size: 0.95rem;
            margin-bottom: 12px;
            line-height: 1.5;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        .email-tags {{
            display: flex;
            gap: 8px;
        }}
        .tag {{
            font-size: 0.75rem;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 4px;
            text-transform: uppercase;
        }}
        .tag-urgency-high {{
            color: #f59e0b;
            border: 1px solid #f59e0b;
        }}
        .tag-urgency-medium {{
            color: #eab308;
            border: 1px solid #eab308;
        }}
        .tag-urgency-low {{
            color: #10b981;
            border: 1px solid #10b981;
        }}
        .tag-urgency-critical {{
            color: #ef4444;
            border: 1px solid #ef4444;
        }}
        .tag-category {{
            background-color: {tag_bg};
            color: {text};
        }}
        
        /* Hiding Streamlit Checkbox Label selectively inside the cards */
        .stCheckbox > label {{
            display: none;
        }}

        /* ── Pill buttons (inactive) — real class from DOM: etjibo410 ── */
        button.etjibo410,
        button[kind="pillsButton"],
        [data-testid="stPillsButton"] {{
            background-color: {card_bg} !important;
            color: {text} !important;
            border: 1px solid {card_border} !important;
        }}
        button.etjibo410:hover {{
            background-color: {tag_bg} !important;
        }}

        /* ── Pill buttons (active/selected) — real class: etjibo411 ── */
        button.etjibo411,
        [data-testid="stPillsButton"][aria-checked="true"] {{
            background-color: #3b82f6 !important;
            color: #ffffff !important;
            border: 1px solid #3b82f6 !important;
        }}

        /* ── All regular buttons including View ── */
        .stButton > button,
        button.etjibo42 {{
            background-color: {card_bg} !important;
            color: {text} !important;
            border: 1px solid {card_border} !important;
        }}
        .stButton > button:hover,
        button.etjibo42:hover {{
            background-color: {tag_bg} !important;
            border-color: #3b82f6 !important;
            color: {text} !important;
        }}

        /* ── Classify button (primary) stays blue ── */
        .stButton > button[data-testid="baseButton-primary"] {{
            background-color: #3b82f6 !important;
            color: #ffffff !important;
            border-color: #3b82f6 !important;
        }}

        /* ── Text Input / Search bar ── */
        [data-testid="stTextInput"] input,
        .stTextInput input {{
            background-color: {card_bg} !important;
            color: {text} !important;
            border: 1px solid {card_border} !important;
            caret-color: {text} !important;
        }}
        [data-testid="stTextInput"] input::placeholder {{
            color: {label_color} !important;
            opacity: 1 !important;
        }}

        /* ── Sidebar radio labels ── */
        [data-testid="stSidebar"] .stRadio label,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
            color: {text} !important;
        }}

        /* ── Metric labels and values ── */
        [data-testid="stMetricValue"],
        [data-testid="stMetricLabel"],
        [data-testid="stMetricDelta"] {{
            color: {text} !important;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
 
inject_custom_css()

# ---------- Prediction Logic ----------

urgent_keywords = ["urgent", "asap", "immediately", "deadline", "priority", "today", "right away"]

def rule_based_urgency(text):
    text = text.lower()
    for word in urgent_keywords:
        if word in text:
            return "high"
    return "low"

def _mock_predict(email_text):
    """Fallback mock prediction used when backend is unavailable."""
    categories = ['Complaint', 'Request', 'Feedback', 'Spam']
    rule_urgency = rule_based_urgency(email_text)
    urg = random.choice(['Critical', 'High']) if rule_urgency == "high" else random.choice(['Medium', 'Low'])
    cat = random.choice(categories)
    conf = random.uniform(0.75, 0.99)
    return cat, urg, conf

def predict_email(email_text, skip_api=False):
    """
    Sends email text to the backend API in the required JSON format:
        { "email": "<email text here>" }
    Returns (category, urgency, confidence).
    Falls back to mock data if backend is unreachable or if skip_api is True.
    """
    if skip_api:
        return _mock_predict(email_text)

    payload = {"email": email_text}
    try:
        # Reduced timeout to 1s for better UX when backend is offline
        response = requests.post(API_URL, json=payload, timeout=1)
        if response.status_code == 200:
            data = response.json()
            return data["category"], data["urgency"], data["confidence"]
        else:
            return _mock_predict(email_text)
    except requests.exceptions.RequestException:
        return _mock_predict(email_text)

# ---------- Data Generation / Loading ----------
@st.cache_data(show_spinner="Generating Mock Emails...")
def load_email_data(num_emails=50):
    data = []
    now = datetime.now()
    
    senders = ["Alice Smith", "Bob Jones", "Charlie Brown", "Diana Prince", "Eve Adams", "Frank Castle", "Grace Lee", "Harry Potter"]
    subjects = [
        "Update required on my account", 
        "Issue with recent billing", 
        "Great service!", 
        "URGENT: Server is down", 
        "Question about pricing", 
        "Feedback on new feature", 
        "Please help me reset my password", 
        "Weekly Newsletter"
    ]
    messages = [
        "Please provide an update asap.",
        "I cannot log into my account. Please fix this.",
        "I really loved the recent changes you made.",
        "The system is down right now! Please fix immediately.",
        "Why was I charged twice this month?",
        "The app is crashing when I click the save button.",
        "How do I reset my credentials?",
        "Here is what happened this week in our company."
    ]

    for i in range(num_emails):
        hours_ago = random.expovariate(1/48) # avg 48 hours ago
        date_time = now - timedelta(hours=hours_ago)
        
        sender = random.choice(senders)
        subj = random.choice(subjects)
        msg_base = random.choice(messages)
        msg = f"{msg_base} " * random.randint(1, 3)
        
        email_full_text = f"{subj}\n\n{msg}"
        # Skip API call during batch generation for performance
        cat, urg, conf = predict_email(email_full_text, skip_api=True)
            
        data.append({
            'ID': f"EML-{10000+i}",
            'Date': date_time,
            'Sender': sender,
            'Subject': subj,
            'Category': cat,
            'Urgency': urg,
            'Snippet': msg[:150] + ('...' if len(msg) > 150 else ''),
            'Message': msg,
            'Read': random.choice([True, False, False]),
        })
            
    df = pd.DataFrame(data)
    if not df.empty:
        df = df.sort_values('Date', ascending=False).reset_index(drop=True)
    return df

if 'df' not in st.session_state:
    st.session_state.df = load_email_data()

df = st.session_state.df

# Initialize selected emails set in session state
if 'selected_emails' not in st.session_state:
    st.session_state.selected_emails = set()

def toggle_email(email_id):
    if email_id in st.session_state.selected_emails:
        st.session_state.selected_emails.remove(email_id)
    else:
        st.session_state.selected_emails.add(email_id)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("""
        <div class="app-title">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg>
            AI Email<br/>Classifier
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-label">FOLDERS</div>', unsafe_allow_html=True)
    
    # We use a radio button to emulate navigation
    folder_counts = {
        'Overview': '',
        'Inbox': f"{len(df)}",
        'Complaint': f"{len(df[df['Category'] == 'Complaint'])}",
        'Request': f"{len(df[df['Category'] == 'Request'])}",
        'Feedback': f"{len(df[df['Category'] == 'Feedback'])}",
        'Spam': f"{len(df[df['Category'] == 'Spam'])}"
    }
    
    # Option names with emojis for styling
    options = ["📊 Overview", "📥 Inbox", "⚠️ Complaint", "📄 Request", "💬 Feedback", "🚫 Spam", "🔍 Classify New"]
    
    # Simple mapping
    folder_map = {
        "📊 Overview": "Overview",
        "📥 Inbox": "Inbox",
        "⚠️ Complaint": "Complaint",
        "📄 Request": "Request",
        "💬 Feedback": "Feedback",
        "🚫 Spam": "Spam",
        "🔍 Classify New": "Classify New",
    }
    
    selected_nav = st.radio("Navigation", options, label_visibility="collapsed")
    current_folder = folder_map[selected_nav]
    
    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    st.markdown("---")
    
    theme_btn_label = "🌞 Light Mode" if st.session_state.theme == 'dark' else "🌙 Dark Mode"
    if st.button(theme_btn_label, width="stretch"):
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.rerun()


# ---------- Main Content ----------

if current_folder == "Overview":
    st.title("📊 Analytics Dashboard")
    st.markdown("Gain insights into email processing and classification metrics.")

    plot_text_color = '#c9d1d9' if st.session_state.theme == 'dark' else '#1f2937'
    plot_template = 'plotly_dark' if st.session_state.theme == 'dark' else 'plotly_white'

    # ── KPI Row ──────────────────────────────────────────────────────────────
    total = len(df)
    unread = len(df[~df['Read']])
    critical_complaints = len(df[(df['Category'] == 'Complaint') & (df['Urgency'] == 'Critical')])
    spam = len(df[df['Category'] == 'Spam'])
    high_urg = len(df[df['Urgency'].isin(['Critical', 'High'])])
    read_rate = f"{(len(df[df['Read']]) / total * 100):.0f}%" if total else "0%"

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("📧 Total Emails", total)
    k2.metric("📬 Unread", unread, delta=f"{unread/total*100:.0f}% unread" if total else "0%")
    k3.metric("🚨 Critical Complaints", critical_complaints)
    k4.metric("⚡ High/Critical Urgency", high_urg)
    k5.metric("🚫 Spam Detected", spam)
    k6.metric("✅ Read Rate", read_rate)

    st.markdown("---")

    # ── Row 1: Category Donut  +  Urgency Bar ──────────────────────────────
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### 🗂️ Category Distribution")
        cat_counts = df['Category'].value_counts().reset_index()
        cat_counts.columns = ['Category', 'Count']
        fig_cat = px.pie(
            cat_counts, values='Count', names='Category', hole=0.45,
            color_discrete_sequence=['#ef4444', '#3b82f6', '#10b981', '#8b949e']
        )
        fig_cat.update_traces(textposition='inside', textinfo='percent+label')
        fig_cat.update_layout(
            template=plot_template,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=plot_text_color), showlegend=False, margin=dict(t=10, b=10)
        )
        st.plotly_chart(fig_cat, width="stretch")

    with c2:
        st.markdown("### ⚡ Urgency Distribution")
        urg_order = ['Critical', 'High', 'Medium', 'Low']
        urg_counts = df['Urgency'].value_counts().reindex(urg_order, fill_value=0).reset_index()
        urg_counts.columns = ['Urgency', 'Count']
        fig_urg = px.bar(
            urg_counts, x='Urgency', y='Count', color='Urgency', text='Count',
            color_discrete_map={'Critical': '#ef4444', 'High': '#f59e0b', 'Medium': '#eab308', 'Low': '#10b981'}
        )
        fig_urg.update_traces(textposition='outside')
        fig_urg.update_layout(
            template=plot_template,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=plot_text_color), showlegend=False,
            margin=dict(t=10, b=10), xaxis_title='', yaxis_title='Emails',
            xaxis=dict(tickfont=dict(color=plot_text_color), title=dict(font=dict(color=plot_text_color))),
            yaxis=dict(tickfont=dict(color=plot_text_color), title=dict(font=dict(color=plot_text_color)))
        )
        st.plotly_chart(fig_urg, width="stretch")

    st.markdown("---")

    # ── Row 2: Heatmap + Top Senders ───────────────────────────────────────
    c3, c4 = st.columns(2)

    with c3:
        st.markdown("### 🔥 Category × Urgency Heatmap")
        heat_df = df.groupby(['Category', 'Urgency']).size().reset_index(name='Count')
        heat_pivot = heat_df.pivot(index='Category', columns='Urgency', values='Count').fillna(0)
        for col in ['Critical', 'High', 'Medium', 'Low']:
            if col not in heat_pivot.columns:
                heat_pivot[col] = 0
        heat_pivot = heat_pivot[['Critical', 'High', 'Medium', 'Low']]
        fig_heat = go.Figure(data=go.Heatmap(
            z=heat_pivot.values,
            x=heat_pivot.columns.tolist(),
            y=heat_pivot.index.tolist(),
            colorscale=[[0, '#eef2ff' if st.session_state.theme == 'light' else '#1e2532'], [0.5, '#f59e0b'], [1, '#ef4444']],
            text=heat_pivot.values.astype(int),
            texttemplate='%{text}',
            showscale=True
        ))
        fig_heat.update_layout(
            template=plot_template,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=plot_text_color), margin=dict(t=10, b=10),
            xaxis_title='Urgency', yaxis_title='Category',
            xaxis=dict(tickfont=dict(color=plot_text_color), title=dict(font=dict(color=plot_text_color))),
            yaxis=dict(tickfont=dict(color=plot_text_color), title=dict(font=dict(color=plot_text_color)))
        )
        st.plotly_chart(fig_heat, width="stretch")

    with c4:
        st.markdown("### 👤 Top Senders")
        top_senders = df['Sender'].value_counts().head(8).reset_index()
        top_senders.columns = ['Sender', 'Emails']
        fig_senders = px.bar(
            top_senders, x='Emails', y='Sender', orientation='h',
            color='Emails', color_continuous_scale=['#3b82f6', '#8b5cf6'], text='Emails'
        )
        fig_senders.update_traces(textposition='outside')
        fig_senders.update_layout(
            template=plot_template,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=plot_text_color), showlegend=False,
            margin=dict(t=10, b=10), yaxis={'categoryorder': 'total ascending', 'tickfont': {'color': plot_text_color}},
            xaxis={'tickfont': {'color': plot_text_color}, 'title': {'font': {'color': plot_text_color}}},
            coloraxis_showscale=False, xaxis_title='Emails', yaxis_title=''
        )
        st.plotly_chart(fig_senders, width="stretch")

    st.markdown("---")

    # ── Row 3: Email Volume Over Time ──────────────────────────────────────
    st.markdown("### 📈 Email Volume Over Time")
    df_temp = df[['Date', 'Category']].copy()
    df_temp['DateOnly'] = df_temp['Date'].dt.date
    time_series_df = df_temp.groupby(['DateOnly', 'Category']).size().reset_index(name='Count')
    time_series_df = time_series_df.sort_values('DateOnly')
    fig_time = px.line(
        time_series_df, x='DateOnly', y='Count', color='Category', markers=True,
        color_discrete_map={'Complaint': '#ef4444', 'Request': '#3b82f6', 'Feedback': '#10b981', 'Spam': '#8b949e'}
    )
    fig_time.update_layout(
        template=plot_template,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=plot_text_color),
        hovermode='x unified', margin=dict(t=10, b=10),
        xaxis=dict(tickfont=dict(color=plot_text_color), title=dict(text='Date', font=dict(color=plot_text_color))),
        yaxis=dict(tickfont=dict(color=plot_text_color), title=dict(text='Number of Emails', font=dict(color=plot_text_color))),
        legend=dict(font=dict(color=plot_text_color))
    )
    st.plotly_chart(fig_time, width="stretch")

    st.markdown("---")

    # ── Row 4: Stacked Urgency Bar + Read vs Unread ────────────────────────
    c5, c6 = st.columns(2)

    with c5:
        st.markdown("### 📊 Urgency Mix per Category")
        stacked = df.groupby(['Category', 'Urgency']).size().reset_index(name='Count')
        fig_stacked = px.bar(
            stacked, x='Category', y='Count', color='Urgency', barmode='stack',
            color_discrete_map={'Critical': '#ef4444', 'High': '#f59e0b', 'Medium': '#eab308', 'Low': '#10b981'}
        )
        fig_stacked.update_layout(
            template=plot_template,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=plot_text_color), margin=dict(t=10, b=10),
            xaxis_title='', yaxis_title='Emails',
            xaxis=dict(tickfont=dict(color=plot_text_color), title=dict(font=dict(color=plot_text_color))),
            yaxis=dict(tickfont=dict(color=plot_text_color), title=dict(font=dict(color=plot_text_color))),
            legend=dict(font=dict(color=plot_text_color))
        )
        st.plotly_chart(fig_stacked, width="stretch")

    with c6:
        st.markdown("### 📬 Read vs Unread")
        read_df = df['Read'].map({True: 'Read', False: 'Unread'}).value_counts().reset_index()
        read_df.columns = ['Status', 'Count']
        fig_read = px.pie(
            read_df, values='Count', names='Status', hole=0.5,
            color_discrete_map={'Read': '#10b981', 'Unread': '#3b82f6'}
        )
        fig_read.update_traces(textposition='inside', textinfo='percent+label')
        fig_read.update_layout(
            template=plot_template,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=plot_text_color), showlegend=False, margin=dict(t=10, b=10)
        )
        st.plotly_chart(fig_read, width="stretch")

elif current_folder == "Classify New":
    st.title("🔍 Classify New Email")
    st.markdown("Use the AI model to predict the category and urgency of a new email.")
    
    email_text = st.text_area("Paste Email Content", height=200, placeholder="Dear Support,\n\nI need an update on my ticket immediately...")
    if st.button("Classify Email", type="primary"):
        if not email_text.strip():
            st.error("Please enter some text to classify.")
        else:
            with st.spinner("Analyzing email (Mock)..."):
                cat, urg, conf = predict_email(email_text)
                st.success("Classification Complete!")
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Category", cat.title())
                
                # Dynamic urgency color
                urg_color = "red" if urg.lower() in ['high', 'critical'] else "orange" if urg.lower() == 'medium' else "green"
                c2.markdown(f"**Urgency**<br><span style='color:{urg_color}; font-size:2rem; font-weight:bold;'>{urg.title()}</span>", unsafe_allow_html=True)
                
                c3.metric("Confidence", f"{conf*100:.1f}%")

else: # Email List View (Inbox, Complaint, etc.)
    # Header
    col_title, col_count = st.columns([4, 1])
    with col_title:
        st.title(f"{current_folder}")
    with col_count:
        st.markdown(f"<div style='text-align: right; margin-top: 1.5rem; color: #8b949e;'>{folder_counts[current_folder]} messages</div>", unsafe_allow_html=True)
    
    # Search
    search_query = st.text_input("Search emails...", placeholder="Search emails...", label_visibility="collapsed")
    
    # Filter Pills
    try:
        # Use native pills if available (Streamlit 1.39+)
        fcol1, fcol2 = st.columns([1, 1])
        with fcol1:
            urgency_filter = st.pills("Urgency", ["All", "Critical", "High", "Medium", "Low"], default="All", label_visibility="collapsed")
        with fcol2:
            date_filter = st.pills("Date", ["Any Date", "Today", "Unread"], default="Any Date", label_visibility="collapsed")
    except AttributeError:
        # Fallback to horizontal radio buttons
        fcol1, fcol2 = st.columns([1, 1])
        with fcol1:
            urgency_filter = st.radio("Urgency", ["All", "Critical", "High", "Medium", "Low"], horizontal=True, label_visibility="collapsed")
        with fcol2:
            date_filter = st.radio("Date", ["Any Date", "Today", "Unread"], horizontal=True, label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Apply Filters
    mask = pd.Series([True] * len(df))
    
    if current_folder != "Inbox":
        mask = mask & (df['Category'] == current_folder)
        
    if search_query:
        query_lower = search_query.lower()
        mask = mask & (
            df['Sender'].str.lower().str.contains(query_lower) | 
            df['Subject'].str.lower().str.contains(query_lower) |
            df['Snippet'].str.lower().str.contains(query_lower)
        )
        
    if urgency_filter and urgency_filter != "All":
        mask = mask & (df['Urgency'] == urgency_filter)
        
    if date_filter == "Today":
        mask = mask & (df['Date'] >= pd.Timestamp(datetime.now().date()))
    elif date_filter == "Unread":
        mask = mask & (~df['Read'])
        
    filtered_df = df[mask]
    
    # Email Dialog
    @st.dialog("Email Details")
    def email_dialog(email_data):
        st.markdown(f"**From:** {email_data['Sender']}")
        st.markdown(f"**Date:** {email_data['Date'].strftime('%Y-%m-%d %I:%M %p')}")
        st.markdown(f"**Subject:** {email_data['Subject']}")
        st.markdown(f"**Category:** {email_data['Category']} | **Urgency:** {email_data['Urgency']}")
        st.divider()
        body = email_data.get('Message', email_data['Snippet'])
        st.markdown(body)
        
    # Display Emails
    for i, row in filtered_df.iterrows():
        # Determine tags styling
        urgency = row['Urgency']
        urgency_class = f"tag-urgency-{urgency.lower()}"
        
        unread_dot = '<div class="unread-dot"></div>' if not row['Read'] else ''
        time_str = row['Date'].strftime('%I:%M %p').lower()
        
        # HTML template for the card (minus the checkbox, which needs to be a Streamlit widget)
        card_html = f"""
        <div class="email-sender">
            {unread_dot} {row['Sender']}
        </div>
        <div class="email-subject">{row['Subject']}</div>
        <div class="email-snippet">{row['Snippet']}</div>
        <div class="email-tags">
            <span class="tag {urgency_class}">{urgency}</span>
            <span class="tag tag-category">{row['Category'].upper()}</span>
        </div>
        """
        
        # Render the card with a standard Streamlit layout
        container = st.container()
        # We manually inject CSS for this specific container to make it look like our card design
        container.markdown('<div class="email-card">', unsafe_allow_html=True)
        
        col1, col2, col3 = container.columns([7, 3, 2])
        
        with col1:
            st.markdown(card_html, unsafe_allow_html=True)
            
        with col2:
             st.markdown(f"<div class='email-time' style='text-align: right; margin-top: 4px;'>{time_str}</div>", unsafe_allow_html=True)
             
        with col3:
             # Add a View button that triggers the dialog
             if st.button("View", key=f"view_{row['ID']}", width="stretch"):
                 # Mark as read when opened (optional, modifying session state dataframe)
                 st.session_state.df.loc[st.session_state.df['ID'] == row['ID'], 'Read'] = True
                 email_dialog(row)
                 
        container.markdown('</div>', unsafe_allow_html=True)

