import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(
    page_title="Agri-Crop Production Dashboard",
    page_icon="🌾",
    layout="wide"
)
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("crop_production.csv")
        df.columns = df.columns.str.strip().str.replace(" ", "_")

    except FileNotFoundError:
        st.warning("⚠️ CSV file not found. Using synthetic data.")

        states = ['Karnataka', 'Maharashtra', 'Punjab',
                  'Uttar Pradesh', 'Tamil Nadu', 'Bihar']
        crops = ['Rice', 'Maize', 'Wheat',
                 'Sugarcane', 'Cotton', 'Groundnut']
        seasons = ['Kharif', 'Rabi', 'Whole Year']
        years = list(range(2015, 2024))

        data = []
        for _ in range(1000):
            state = np.random.choice(states)
            crop = np.random.choice(crops)
            year = np.random.choice(years)
            season = np.random.choice(seasons)
            area = np.random.randint(100, 10000)

            yield_factor = {
                'Rice': 3,
                'Wheat': 3.5,
                'Maize': 4,
                'Sugarcane': 60,
                'Cotton': 0.5,
                'Groundnut': 1.5
            }

            production = area * yield_factor[crop] * np.random.uniform(0.8, 1.2)

            data.append([state, year, season, crop, area, round(production, 2)])

        df = pd.DataFrame(
            data,
            columns=['State_Name', 'Crop_Year', 'Season',
                     'Crop', 'Area', 'Production']
        )

    return df
df = load_data()
st.sidebar.header("Filter Options")
all_years = sorted(df['Crop_Year'].unique())
selected_year = st.sidebar.selectbox(
    "Select Year", all_years, index=len(all_years) - 1
)
all_states = sorted(df['State_Name'].unique())
selected_state = st.sidebar.multiselect(
    "Select State(s)", all_states, default=all_states[:2]
)
all_crops = sorted(df['Crop'].unique())
selected_crops = st.sidebar.multiselect(
    "Select Crop(s)", all_crops, default=all_crops[:3]
)
filtered_df = df[
    (df['Crop_Year'] == selected_year) &
    (df['State_Name'].isin(selected_state)) &
    (df['Crop'].isin(selected_crops))
]
st.title("🌾 Agricultural Crop Production Analysis")
st.markdown("Analyze crop trends, production yields, and agricultural distribution.")
total_production = filtered_df['Production'].sum()
total_area = filtered_df['Area'].sum()
avg_yield = total_production / total_area if total_area > 0 else 0

c1, c2, c3 = st.columns(3)
c1.metric("Total Production (Tonnes)", f"{total_production:,.0f}")
c2.metric("Total Cultivated Area (Hectares)", f"{total_area:,.0f}")
c3.metric("Avg Yield (Tonnes/Hectare)", f"{avg_yield:.2f}")

st.markdown("---")
v1, v2 = st.columns(2)

with v1:
    st.subheader("📊 Production by Crop")
    fig_crop = px.bar(
        filtered_df.groupby('Crop')['Production'].sum().reset_index(),
        x='Crop',
        y='Production',
        color='Crop',
        title=f"Total Production in {selected_year}",
        template="plotly_white"
    )
    st.plotly_chart(fig_crop, use_container_width=True)

with v2:
    st.subheader("🌍 State-wise Contribution")
    fig_state = px.pie(
        filtered_df,
        values='Production',
        names='State_Name',
        title=f"Production Share by State in {selected_year}",
        hole=0.4
    )
    st.plotly_chart(fig_state, use_container_width=True)
v3, v4 = st.columns(2)

with v3:
    st.subheader("📈 Trend Over Time")
    history_df = df[
        (df['State_Name'].isin(selected_state)) &
        (df['Crop'].isin(selected_crops))
    ]

    yearly_prod = history_df.groupby(
        ['Crop_Year', 'State_Name']
    )['Production'].sum().reset_index()

    fig_trend = px.line(
        yearly_prod,
        x='Crop_Year',
        y='Production',
        color='State_Name',
        markers=True,
        title="Production Trend (All Years)"
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with v4:
    st.subheader("📉 Area vs Production")
    fig_scatter = px.scatter(
        filtered_df,
        x='Area',
        y='Production',
        color='Crop',
        size='Area',
        hover_data=['State_Name'],
        title="Area vs Production Relationship"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
with st.expander("📄 View Detailed Data"):
    st.dataframe(filtered_df)
