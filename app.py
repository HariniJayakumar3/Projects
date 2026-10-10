
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
from google import genai
from pathlib import Path

load_dotenv()

st.set_page_config(
    page_title="GCC Compass",
    page_icon="🧭",
    layout="wide"
)
from pathlib import Path
# Load company records from the data folder
companies_path = Path(__file__).parent / "data" / "companies.csv"

df = pd.read_csv(companies_path).fillna("")


# Sidebar filters
st.sidebar.title("Explore GCCs")

city_options = ["All cities"] + sorted(df["City"].unique())
industry_options = ["All industries"] + sorted(
    df["Industry"].unique()
)

selected_city = st.sidebar.selectbox(
    "Select city", city_options
)

selected_industry = st.sidebar.selectbox(
    "Select industry", industry_options
)

search = st.sidebar.text_input("Search company")

# Apply filters
filtered = df.copy()

if selected_city != "All cities":
    filtered = filtered[
        filtered["City"] == selected_city
    ]

if selected_industry != "All industries":
    filtered = filtered[
        filtered["Industry"] == selected_industry
    ]

if search.strip():
    filtered = filtered[
        filtered["Company"].str.contains(
            search.strip(), case=False, na=False
        )
    ]

# ========== GCC COMPASS OVERVIEW ==========

with st.container(border=True):

    st.markdown(
        """
        <div style="
            background: linear-gradient(120deg, #12304A, #176B87);
            padding: 24px;
            border-radius: 12px;
            margin-bottom: 20px;
        ">
            <p style="color:#A5F3FC; font-size:13px;
                      letter-spacing:2px; margin-bottom:6px;">
                INDIA GCC INTELLIGENCE PLATFORM
            </p>
            <h1 style="color:white; margin:0;">
                🧭 GCC Compass
            </h1>
            <p style="color:#E0F2FE; font-size:16px; margin-top:10px;">
                Explore companies, locations and business functions
                across India's GCC ecosystem.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "Prototype dataset: illustrative sample only. "
        "Company records and GCC classifications require verification."
    )

    st.markdown(
        """
        <h2 style="margin-top:24px;">📍 GCC Locations Across India</h2>
        <p style="color:#A1A1AA;">
            Explore the cities currently represented in the prototype.
        </p>
        """,
        unsafe_allow_html=True,
    )

    city_map = pd.DataFrame({
    "City": [
        "Bengaluru",
        "Chennai",
        "Hyderabad",
        "Pune",
        "Gurugram",
        "Noida",
        "Mumbai",
        "Kolkata",
        "Kochi",
        "Visakhapatnam",
        "Delhi",
    ],
    "latitude": [
        12.9716, 13.0827, 17.3850, 18.5204,
        28.4595, 28.5355, 19.0760, 22.5726,
        9.9312, 17.6868, 28.6139,
    ],
    "longitude": [
        77.5946, 80.2707, 78.4867, 73.8567,
        77.0266, 77.3910, 72.8777, 88.3639,
        76.2673, 83.2185, 77.2090,
    ],
})

    st.map(
        city_map,
        latitude="latitude",
        longitude="longitude",
        zoom=4,
        height=400,
    )

    st.caption(
        "📌 City-level markers only; they do not indicate verified "
        "individual company office addresses."
    )

# ========== END GCC COMPASS OVERVIEW ==========



col1, col2, col3 = st.columns(3)

col1.metric("Companies in sample", len(df))
col2.metric("Cities represented", df["City"].nunique())
col3.metric("Matching companies", len(filtered))

st.divider()

left, right = st.columns([3, 2])

with left:
    st.subheader("GCC Company Explorer")
    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True
    )

with right:
    st.subheader("Companies by City")
    city_counts = (
        filtered.groupby("City")
        .size()
        .reset_index(name="Companies")
    )

    if not city_counts.empty:
        fig = px.bar(
            city_counts,
            x="City",
            y="Companies",
            color="City",
            title="Matching sample records by city"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No companies match your filters.")

# Company Profile Explorer
st.divider()
st.header("🏢 Company Profile Explorer")
st.write(
    "Inspect company records, listed locations, business functions "
    "and supporting source references."
)

company_names = sorted(df["Company"].dropna().unique().tolist())

selected_company = st.selectbox(
    "Select a company to explore",
    company_names,
    key="profile_company"
)

company_records = df[df["Company"] == selected_company].copy()

if not company_records.empty:
    first_record = company_records.iloc[0]

    profile1, profile2, profile3 = st.columns(3)

    profile1.metric("Listed locations", company_records["City"].nunique())
    profile2.metric("Industries listed", company_records["Industry"].nunique())
    profile3.metric("Records found", len(company_records))

    st.subheader(selected_company + " — Overview")

    st.dataframe(
        company_records[
            ["City", "Industry", "Function", "Centre Type"]
        ].drop_duplicates(),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Source and verification")

    for _, record in company_records.drop_duplicates(
        subset=["Source URL", "City"]
    ).iterrows():
        with st.container(border=True):
            st.markdown("**Location:** " + str(record["City"]))
            st.markdown("**Location evidence source**")

            source_url = str(record["Source URL"]).strip()
            status = str(record["Verification Status"]).strip()

            st.markdown("**Verification status:** " + status)

            if source_url.startswith(("https://", "http://")):
                st.markdown(
                    "[↗ View supporting evidence](" + source_url + ")"
                )
            else:
                st.warning("No valid source link is available.")

    st.caption(
        "A source listing does not independently confirm current office "
        "status or prove every detail in a record. Verify each location "
        "before using it for business decisions."
    )




# GCC City Comparator — Evidence-aware version
st.divider()
st.header("📊 GCC City Comparator")

st.write(
    "Compare potential GCC locations across decision factors. "
    "The platform distinguishes available company data from "
    "market indicators that still need reliable sources."
)

# Use the cities present in the company dataset
available_cities = sorted(df["City"].dropna().unique().tolist())

if len(available_cities) >= 2:
    col1, col2 = st.columns(2)

    with col1:
        city_a = st.selectbox(
            "First city",
            available_cities,
            index=0,
            key="compare_city_a"
        )

    with col2:
        default_b = 1 if len(available_cities) > 1 else 0
        city_b = st.selectbox(
            "Second city",
            available_cities,
            index=default_b,
            key="compare_city_b"
        )

    if city_a == city_b:
        st.warning("Choose two different cities to compare.")
    else:
        city_a_records = df[df["City"] == city_a]
        city_b_records = df[df["City"] == city_b]

        st.subheader(f"{city_a} vs {city_b}")

        # Company coverage based on the current dataset
        overview = pd.DataFrame({
            "Indicator": [
                "Companies listed in prototype",
                "Industries represented",
                "Distinct business functions",
            ],
            city_a: [
                city_a_records["Company"].nunique(),
                city_a_records["Industry"].nunique(),
                city_a_records["Function"].nunique(),
            ],
            city_b: [
                city_b_records["Company"].nunique(),
                city_b_records["Industry"].nunique(),
                city_b_records["Function"].nunique(),
            ],
        })

        st.markdown("#### Company ecosystem in this dataset")
        st.dataframe(
            overview,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "These counts describe records in the current prototype only. "
            "They are not total market counts for either city."
        )

        # Decision factors that require separate market evidence
        
        
        # Load and display market indicators in a compact comparison
        indicators_path = (
            Path(__file__).parent
            / "data"
            / "gcc_compass_market_indicators.csv"
        )

        st.markdown("#### Market indicators")

        if indicators_path.exists():
            indicators_df = pd.read_csv(
                indicators_path
            ).fillna("")

            selected_indicators = indicators_df[
                indicators_df["city"].isin([city_a, city_b])
            ].copy()

            def format_indicator(record):
                value = str(record["value"]).strip()
                unit = str(record["unit"]).strip()
                period = str(record["period"]).strip()
                status = str(record["evidence_status"]).strip()

                if not value:
                    value_text = "Not yet available"
                else:
                    value_text = value
                    if unit and unit.lower() != "policy":
                        value_text += f" {unit}"

                if status == "Source-reported":
                    status_text = "Source-reported"
                elif "official" in status.lower():
                    status_text = "Verification pending"
                elif "needs" in status.lower():
                    status_text = "Needs verification"
                else:
                    status_text = status or "Status unknown"

                details = [value_text, status_text]

                if period:
                    details.append(period)

                return " · ".join(details)

            comparison_rows = []

            for factor in selected_indicators[
                "decision_factor"
            ].drop_duplicates():
                factor_rows = selected_indicators[
                    selected_indicators["decision_factor"] == factor
                ]

                city_values = {}

                for city in [city_a, city_b]:
                    city_record = factor_rows[
                        factor_rows["city"] == city
                    ]

                    if city_record.empty:
                        city_values[city] = "Not yet available"
                    else:
                        city_values[city] = format_indicator(
                            city_record.iloc[0]
                        )

                comparison_rows.append({
                    "Decision factor": factor,
                    city_a: city_values[city_a],
                    city_b: city_values[city_b],
                })

            comparison_table = pd.DataFrame(comparison_rows)

            st.dataframe(
                comparison_table,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Decision factor": st.column_config.TextColumn(
                        width="medium"
                    ),
                    city_a: st.column_config.TextColumn(
                        width="large"
                    ),
                    city_b: st.column_config.TextColumn(
                        width="large"
                    ),
                },
            )

            with st.expander(
                "View source links and verification notes"
            ):
                for factor in selected_indicators[
                    "decision_factor"
                ].drop_duplicates():
                    st.markdown(f"**{factor}**")

                    factor_rows = selected_indicators[
                        selected_indicators["decision_factor"] == factor
                    ]

                    for _, record in factor_rows.iterrows():
                        city_name = str(record["city"])
                        source_name = str(record["source_name"]).strip()
                        source_url = str(record["source_url"]).strip()
                        note = str(record["source_note"]).strip()

                        st.markdown(f"**{city_name}**")

                        if source_url.startswith(("https://", "http://")):
                            st.markdown(
                                f"[{source_name or 'Open source'}]"
                                f"({source_url})"
                            )
                        else:
                            st.caption("No source URL available.")

                        if note:
                            st.caption(note)

        else:
            st.warning(
                "Market indicators file not found. "
                "Check that it is saved in your data folder."
            )



        st.markdown("#### Companies listed for each city")

        left, right = st.columns(2)

        with left:
            st.markdown(f"**{city_a}**")
            st.dataframe(
                city_a_records[
                    ["Company", "Industry", "Function"]
                ].drop_duplicates(),
                use_container_width=True,
                hide_index=True
            )

        with right:
            st.markdown(f"**{city_b}**")
            st.dataframe(
                city_b_records[
                    ["Company", "Industry", "Function"]
                ].drop_duplicates(),
                use_container_width=True,
                hide_index=True
            )

else:
    st.warning("At least two cities are needed for comparison.")

# -----------------------------------------
# GCC Compass - Enhanced Research Assistant
# -----------------------------------------

from pathlib import Path

st.divider()
st.header("🔎 GCC Research Assistant")
st.write(
    "Explore GCC market intelligence, inspect supporting evidence, "
    "and trace important claims to their original sources."
)

research_path = Path(__file__).parent / "data" / "research.csv"

if research_path.exists():
    research_df = pd.read_csv(research_path).fillna("")

    required_columns = [
        "topic", "fact", "source_name", "source_url"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in research_df.columns
    ]

    if missing_columns:
        st.error(
            "Missing columns in research.csv: "
            + ", ".join(missing_columns)
        )
    elif research_df.empty:
        st.info("Add research records to begin.")
    else:
        # Support optional metadata columns
        if "publication_date" not in research_df.columns:
            research_df["publication_date"] = ""

        if "category" not in research_df.columns:
            research_df["category"] = "General"

        col1, col2 = st.columns([3, 1])

        with col1:
            question = st.text_input(
                "What would you like to research?",
                placeholder=(
                    "e.g. What does the evidence say about "
                    "India's GCC market outlook?"
                ),
                key="enhanced_gcc_question"
            )

        with col2:
            st.write("")
            st.write("")
            search_clicked = st.button(
                "Find evidence",
                type="primary",
                use_container_width=True
            )

        if search_clicked:
            if not question.strip():
                st.warning("Please enter a research question.")
            else:
                import re

                stop_words = {
                    "the", "and", "for", "with", "what", "when",
                    "where", "which", "who", "does", "from", "that",
                    "this", "are", "was", "how", "can", "could",
                    "would", "should", "about", "into", "have",
                    "has", "its", "their", "they", "will"
                }

                terms = [
                    word for word in re.findall(
                        r"[a-zA-Z0-9]+",
                        question.lower()
                    )
                    if len(word) > 2 and word not in stop_words
                ]

                searchable = (
                    research_df["topic"].astype(str) + " " +
                    research_df["fact"].astype(str) + " " +
                    research_df["category"].astype(str)
                ).str.lower()

                def score_record(text):
                    # Count distinct matching terms
                    return sum(
                        1 for term in set(terms)
                        if term in text
                    )

                scores = searchable.apply(score_record)

                results = research_df.loc[scores > 0].copy()
                results["Relevance"] = scores.loc[scores > 0]

                results = results.sort_values(
                    "Relevance",
                    ascending=False
                ).head(5)

                if results.empty:
                    st.info(
                        "No matching records were found. Try terms such "
                        "as GCC market, Tamil Nadu policy, definition, "
                        "or market outlook."
                    )
                else:
                    st.subheader("Research findings")
                    
                    # Gemini AI research summary
                    api_key = os.getenv("GEMINI_API_KEY")

                    if api_key:
                        evidence_parts = []

                        for number, (_, record) in enumerate(
                            results.iterrows(), start=1
                        ):
                            evidence_parts.append(
                                f"[{number}]\n"
                                f"Topic: {record['topic']}\n"
                                f"Fact: {record['fact']}\n"
                                f"Source: {record['source_name']}\n"
                                f"URL: {record['source_url']}"
                            )

                        evidence_text = "\n\n".join(evidence_parts)

                        prompt = f"""
You are the GCC Compass research assistant.

Answer the user's question using only the evidence below.
Do not invent facts, numbers, or sources.
Cite evidence using [1], [2], etc.
Distinguish historical figures from forecasts.
If the evidence is insufficient, say so.
Keep the answer concise.

Question:
{question}

Evidence:
{evidence_text}
"""

                        try:
                            client = genai.Client(api_key=api_key)

                            with st.spinner(
                                "Gemini is analyzing the evidence..."
                            ):
                                response = client.models.generate_content(
                                    model="gemini-2.5-flash",
                                    contents=prompt,
                                )

                            if response.text:
                                st.markdown("### 🤖 AI Research Summary")
                                st.markdown(response.text)
                            else:
                                st.warning(
                                    "Gemini returned an empty response."
                                )

                        except Exception as error:
                            st.error(
                                "Gemini could not generate the summary."
                            )
                            st.caption(str(error))
                        else:
                            st.info(
                            "Gemini is not configured. Check your .env file."
                        )

                    metric1, metric2 = st.columns(2)
                    metric1.metric(
                        "Relevant records",
                        len(results)
                    )
                    metric2.metric(
                        "Records with source links",
                        sum(
                            str(url).strip().startswith(
                                ("https://", "http://")
                            )
                            for url in results["source_url"]
                        )
                    )

                    st.caption(
                        "Results are ranked by keyword overlap. "
                        "A match does not mean the source independently "
                        "verifies every statement."
                    )

                    for _, row in results.iterrows():
                        with st.container(border=True):
                            st.markdown(f"### {row['topic']}")

                            category = str(
                                row["category"]
                            ).strip()

                            pub_date = str(
                                row["publication_date"]
                            ).strip()

                            st.caption(
                                f"Category: {category or 'General'}"
                                + (
                                    f" · Published: {pub_date}"
                                    if pub_date else ""
                                )
                            )

                            st.write(row["fact"])

                            st.divider()

                            source_name = str(
                                row["source_name"]
                            ).strip()

                            source_url = str(
                                row["source_url"]
                            ).strip()

                            st.markdown(
                                f"**Source:** "
                                f"{source_name or 'Not provided'}"
                            )

                            if source_url.startswith(
                                ("https://", "http://")
                            ):
                                st.markdown(
                                    f"[↗ Open original source]({source_url})"
                                )
                                st.caption(
                                    "Open the original publication to "
                                    "verify its context and methodology."
                                )
                            else:
                                st.warning(
                                    "No source URL is available for "
                                    "this record."
                                )

                    st.info(
                        "Research limitation: this prototype searches "
                        "your local dataset. It does not automatically "
                        "retrieve new reports from the internet."
                    )
else:
    st.error(
        "Research file not found. Ensure that data/research.csv exists."
    )
