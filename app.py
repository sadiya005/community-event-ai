import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd
import plotly.express as px
import re

st.set_page_config(
    page_title="CommunityOps AI",
    page_icon="🧠",
    layout="wide"
)

st.sidebar.title("CommunityOps AI")
st.sidebar.markdown("AI-Powered Event Planning Assistant")
st.sidebar.markdown("---")
st.sidebar.info("Generate AI-powered event plans with operational insights.")

st.markdown("""
<style>
.main {
    background-color: #f5f7fa;
}

.stTabs [data-baseweb="tab"] {
    font-size: 18px;
    font-weight: 600;
}

.stMetric {
    background-color: white;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
}

.block-container {
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
}
h1 {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)



def create_pdf(text):
    file_path = "event_plan.pdf"
    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()
    elements = []

    for line in text.split("\n"):
        elements.append(Paragraph(line, styles["Normal"]))

    doc.build(elements)
    return file_path


if "output" not in st.session_state:
    st.session_state.output = None

if "readiness_score" not in st.session_state:
    st.session_state.readiness_score = 0


# Load API key
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="Community Event AI Planner", layout="wide")

st.title("CommunityOps AI Planner")
st.write("Generate structured operational plans for community events using AI.")

# Sidebar Inputs
st.sidebar.header("Event Details")

event_type = st.sidebar.text_input("Event Type", "Blood Donation Camp")
volunteers = st.sidebar.number_input("Number of Volunteers", min_value=1, value=12)
budget = st.sidebar.text_input("Total Budget", "₹50,000")
location = st.sidebar.selectbox("Location Type", ["Urban", "Rural", "Semi-Urban"])
target_audience = st.sidebar.number_input("Target Audience", min_value=10, value=200)
event_date = st.sidebar.text_input("Event Date", "March 15")
detail_level = st.sidebar.selectbox("Detail Level", ["Basic", "Detailed", "Highly Detailed"])
tone = st.sidebar.selectbox("Tone", ["Professional", "Friendly", "Formal"])

generate = st.sidebar.button("Generate Event Plan")

def generate_plan():
    prompt = f"""
    You are an expert community operations planner.

    Create a structured event plan with the following sections:

    1. Event Overview
    2. Volunteer Allocation
    3. Timeline
    4. Budget Breakdown
    5. Announcement Draft
    6. Risk Checklist
    7. Operational Readiness Score (0-100)

    Event Details:
    Event Type: {event_type}
    Volunteers Available: {volunteers}
    Budget: {budget}
    Location Type: {location}
    Target Audience: {target_audience}
    Event Date: {event_date}

    Detail Level: {detail_level}
    Tone: {tone}

    IMPORTANT:
    At the end, clearly mention:
    Readiness Score: <number only>
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You generate structured event plans."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    result = response.choices[0].message.content
    st.session_state.output = result

    # Extract readiness score
    import re
    match = re.search(r"Readiness Score:\s*(\d+)", result)
    if match:
        st.session_state.readiness_score = int(match.group(1))


if generate:
    with st.spinner("Generating AI Event Plan..."):
        generate_plan()

if st.session_state.output:

    full_text = st.session_state.output

    # Split by section numbers
    sections = full_text.split("**")

    tabs = st.tabs([
        "Full Plan 📄",
        "Metrics & Charts 📊"
    ])

    # ---- TAB 1: FULL PLAN ----
    with tabs[0]:
        st.markdown(full_text)

    # ---- TAB 2: VISUAL ANALYTICS ----
    with tabs[1]:

        col1, col2, col3 = st.columns(3)

        col1.metric("Target Audience", target_audience)
        col2.metric("Total Volunteers", volunteers)
        col3.metric("Total Budget", budget)


        st.markdown("## Operational Readiness Score")
        score = st.session_state.readiness_score

        st.markdown("### AI Operational Readiness")

        st.progress(score / 100)

        if score >= 85:
            st.success(f"Excellent Readiness: {score}/100")
        elif score >= 70:
            st.info(f"Good Readiness: {score}/100")
        else:
            st.warning(f"Needs Improvement: {score}/100")

        st.metric("Readiness Score", f"{st.session_state.readiness_score}/100")

        import pandas as pd
        import plotly.express as px
        import re

        # Volunteer vs Audience Chart
        st.markdown("### Volunteer Capacity Analysis")

        vol_df = pd.DataFrame({
            "Category": ["Volunteers", "Target Audience"],
            "Count": [volunteers, target_audience]
        })

        st.bar_chart(vol_df.set_index("Category"))
        st.markdown("### 🔎 Key Insights")

        if score >= 85:
            st.success("The operational plan demonstrates high readiness and low execution risk.")
        elif score >= 70:
            st.info("The event is well-structured, with minor optimization opportunities.")
        else:
            st.warning("Further planning adjustments may enhance operational readiness.")

        st.markdown("""
        - Volunteer roles are clearly distributed to avoid bottlenecks.
        - Workforce capacity aligns with expected event turnout.
        - Defined timelines improve coordination efficiency.
        - Monitoring execution metrics can further enhance outcomes.
        """)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Regenerate Plan"):
            generate_plan()
            st.rerun()

    with col2:
        if st.session_state.output:

            pdf_path = create_pdf(st.session_state.output)

            with open(pdf_path, "rb") as file:
                st.download_button(
                    label="⬇ Download as PDF",
                    data=file,
                    file_name="event_plan.pdf",
                    mime="application/pdf"
                )
