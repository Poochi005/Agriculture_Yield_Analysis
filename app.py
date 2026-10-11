from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Agriculture Yield Analysis", page_icon="🌾", layout="wide")

ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "agriculture_yield.csv"

REQUIRED_COLUMNS = [
    "Year", "State", "Crop", "Area_Hectares", "Production_Tonnes",
    "Rainfall_mm", "Fertilizer_kg_per_hectare", "Yield_Tonnes_per_Hectare"
]

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError("CSV is missing required columns: " + ", ".join(missing))
    for col in REQUIRED_COLUMNS:
        if col in ["State", "Crop"]:
            df[col] = df[col].astype(str).str.strip()
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.dropna(subset=REQUIRED_COLUMNS)

st.title("🌾 Agriculture Yield Analysis")
st.caption("Interactive crop production, yield, rainfall and fertilizer dashboard")
st.info("Demo dataset: the included rows are illustrative sample data, not official agricultural statistics.")

uploaded = st.sidebar.file_uploader("Optional: upload your own CSV", type=["csv"])
try:
    if uploaded is not None:
        data = pd.read_csv(uploaded)
        missing = [c for c in REQUIRED_COLUMNS if c not in data.columns]
        if missing:
            st.error("Uploaded CSV is missing columns: " + ", ".join(missing))
            st.stop()
        for col in REQUIRED_COLUMNS:
            if col in ["State", "Crop"]:
                data[col] = data[col].astype(str).str.strip()
            else:
                data[col] = pd.to_numeric(data[col], errors="coerce")
        data = data.dropna(subset=REQUIRED_COLUMNS)
    else:
        data = load_data(str(DATA_PATH))
except Exception as exc:
    st.error(f"Could not load dataset: {exc}")
    st.stop()

if data.empty:
    st.warning("No valid rows found in the dataset.")
    st.stop()

st.sidebar.header("Filters")
years = sorted(data["Year"].dropna().astype(int).unique().tolist())
crops = sorted(data["Crop"].unique().tolist())
states = sorted(data["State"].unique().tolist())
year_range = st.sidebar.select_slider(
    "Year range", options=years, value=(years[0], years[-1])
) if len(years) > 1 else (years[0], years[0])
selected_crops = st.sidebar.multiselect("Crop", crops, default=crops)
selected_states = st.sidebar.multiselect("State", states, default=states)

filtered = data[
    data["Year"].between(year_range[0], year_range[1])
    & data["Crop"].isin(selected_crops)
    & data["State"].isin(selected_states)
]
if filtered.empty:
    st.warning("No rows match the selected filters. Change the filters in the sidebar.")
    st.stop()

total_production = filtered["Production_Tonnes"].sum()
avg_yield = filtered["Yield_Tonnes_per_Hectare"].mean()
total_area = filtered["Area_Hectares"].sum()
avg_rainfall = filtered["Rainfall_mm"].mean()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Production", f"{total_production:,.0f} tonnes")
c2.metric("Average Yield", f"{avg_yield:,.2f} t/ha")
c3.metric("Cultivated Area", f"{total_area:,.0f} ha")
c4.metric("Average Rainfall", f"{avg_rainfall:,.0f} mm")

left, right = st.columns(2)
with left:
    crop_summary = filtered.groupby("Crop", as_index=False).agg(
        Yield=("Yield_Tonnes_per_Hectare", "mean"),
        Production=("Production_Tonnes", "sum")
    )
    fig = px.bar(crop_summary, x="Crop", y="Yield", color="Crop",
                 title="Average Yield by Crop", labels={"Yield": "Yield (tonnes/hectare)"})
    st.plotly_chart(fig, use_container_width=True)
with right:
    year_summary = filtered.groupby("Year", as_index=False)["Production_Tonnes"].sum()
    fig = px.line(year_summary, x="Year", y="Production_Tonnes", markers=True,
                  title="Year-wise Total Production")
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    fig = px.scatter(filtered, x="Rainfall_mm", y="Yield_Tonnes_per_Hectare",
                     color="Crop", hover_data=["State", "Year"],
                     title="Rainfall vs Yield")
    st.plotly_chart(fig, use_container_width=True)
with right:
    fig = px.scatter(filtered, x="Fertilizer_kg_per_hectare",
                     y="Yield_Tonnes_per_Hectare", color="Crop",
                     hover_data=["State", "Year"], title="Fertilizer Usage vs Yield")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Filtered agriculture records")
st.dataframe(filtered.sort_values(["Year", "State", "Crop"]), use_container_width=True, hide_index=True)
st.download_button(
    "Download filtered CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="agriculture_yield_filtered.csv",
    mime="text/csv"
)
