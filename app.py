
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


st.set_page_config(
    page_title="Agriculture Yield Analysis",
    page_icon="🌾",
    layout="wide",
)

ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "agriculture_yield.csv"

REQUIRED_COLUMNS = [
    "Year",
    "State",
    "Crop",
    "Area_Hectares",
    "Production_Tonnes",
    "Rainfall_mm",
    "Fertilizer_kg_per_hectare",
    "Yield_Tonnes_per_Hectare",
]

CATEGORICAL = ["State", "Crop"]
NUMERIC = [
    "Year",
    "Area_Hectares",
    "Rainfall_mm",
    "Fertilizer_kg_per_hectare",
]
FEATURES = NUMERIC + CATEGORICAL
TARGET = "Yield_Tonnes_per_Hectare"


def clean_data(df):
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            "CSV is missing required columns: " + ", ".join(missing)
        )

    df = df[REQUIRED_COLUMNS].copy()

    for col in CATEGORICAL:
        df[col] = df[col].astype("string").str.strip()

    for col in REQUIRED_COLUMNS:
        if col not in CATEGORICAL:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=REQUIRED_COLUMNS)
    df = df[df["State"].ne("") & df["Crop"].ne("")]
    return df.reset_index(drop=True)


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    return clean_data(pd.read_csv(path))


def build_model():
    preprocess = ColumnTransformer(
        transformers=[
            (
                "categories",
                OneHotEncoder(handle_unknown="ignore"),
                CATEGORICAL,
            ),
            ("numbers", "passthrough", NUMERIC),
        ]
    )

    return Pipeline(
        steps=[
            ("preprocess", preprocess),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=100,
                    random_state=42,
                ),
            ),
        ]
    )


st.title("🌾 Agriculture Yield Analysis")
st.caption(
    "Interactive crop production, yield, rainfall and fertilizer dashboard"
)
st.info(
    "Demo dataset: the included rows are illustrative sample data, "
    "not official agricultural statistics."
)

uploaded = st.sidebar.file_uploader(
    "Optional: upload your own CSV",
    type=["csv"],
)

try:
    if uploaded is not None:
        data = clean_data(pd.read_csv(uploaded))
    else:
        data = load_data(str(DATA_PATH))
except Exception as exc:
    st.error(f"Could not load dataset: {exc}")
    st.stop()

if data.empty:
    st.warning("No valid rows found in the dataset.")
    st.stop()


# ---------------- DASHBOARD FILTERS ----------------

st.sidebar.header("Filters")

years = sorted(data["Year"].astype(int).unique().tolist())
crops = sorted(data["Crop"].unique().tolist())
states = sorted(data["State"].unique().tolist())

if len(years) > 1:
    year_range = st.sidebar.select_slider(
        "Year range",
        options=years,
        value=(years[0], years[-1]),
    )
else:
    year_range = (years[0], years[0])

selected_crops = st.sidebar.multiselect(
    "Crop", crops, default=crops
)
selected_states = st.sidebar.multiselect(
    "State", states, default=states
)

filtered = data[
    data["Year"].between(year_range[0], year_range[1])
    & data["Crop"].isin(selected_crops)
    & data["State"].isin(selected_states)
]

if filtered.empty:
    st.warning(
        "No rows match the selected filters. Change the filters in the sidebar."
    )
    st.stop()


# ---------------- DASHBOARD METRICS ----------------

total_production = filtered["Production_Tonnes"].sum()
avg_yield = filtered["Yield_Tonnes_per_Hectare"].mean()
total_area = filtered["Area_Hectares"].sum()
avg_rainfall = filtered["Rainfall_mm"].mean()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Production", f"{total_production:,.0f} tonnes")
c2.metric("Average Yield", f"{avg_yield:,.2f} t/ha")
c3.metric("Cultivated Area", f"{total_area:,.0f} ha")
c4.metric("Average Rainfall", f"{avg_rainfall:,.0f} mm")


# ---------------- DASHBOARD CHARTS ----------------

left, right = st.columns(2)

with left:
    crop_summary = filtered.groupby("Crop", as_index=False).agg(
        Yield=("Yield_Tonnes_per_Hectare", "mean"),
        Production=("Production_Tonnes", "sum"),
    )
    fig = px.bar(
        crop_summary,
        x="Crop",
        y="Yield",
        color="Crop",
        title="Average Yield by Crop",
        labels={"Yield": "Yield (tonnes/hectare)"},
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    year_summary = filtered.groupby("Year", as_index=False)[
        "Production_Tonnes"
    ].sum()
    fig = px.line(
        year_summary,
        x="Year",
        y="Production_Tonnes",
        markers=True,
        title="Year-wise Total Production",
    )
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)

with left:
    fig = px.scatter(
        filtered,
        x="Rainfall_mm",
        y="Yield_Tonnes_per_Hectare",
        color="Crop",
        hover_data=["State", "Year"],
        title="Rainfall vs Yield",
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    fig = px.scatter(
        filtered,
        x="Fertilizer_kg_per_hectare",
        y="Yield_Tonnes_per_Hectare",
        color="Crop",
        hover_data=["State", "Year"],
        title="Fertilizer Usage vs Yield",
    )
    st.plotly_chart(fig, use_container_width=True)


st.subheader("Filtered agriculture records")
st.dataframe(
    filtered.sort_values(["Year", "State", "Crop"]),
    use_container_width=True,
    hide_index=True,
)

st.download_button(
    "Download filtered CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="agriculture_yield_filtered.csv",
    mime="text/csv",
)


# ---------------- MACHINE LEARNING ----------------

st.divider()
st.header("🤖 Machine Learning - Crop Yield Prediction")
st.write(
    "Predict estimated crop yield using the available agriculture records."
)

st.warning(
    "The included dataset is illustrative sample data. "
    "Predictions and evaluation metrics are for demonstration only."
)

ml_data = data[FEATURES + [TARGET]].copy()
ml_data = ml_data.replace([np.inf, -np.inf], np.nan).dropna()
ml_data = ml_data[
    (ml_data["Area_Hectares"] > 0)
    & (ml_data["Yield_Tonnes_per_Hectare"] >= 0)
].reset_index(drop=True)

if len(ml_data) < 8:
    st.warning(
        f"Only {len(ml_data)} valid rows are available. "
        "At least 8 rows are required for this demonstration. "
        "Use a larger verified dataset for meaningful evaluation."
    )
else:
    # Hold-out test evaluation
    X = ml_data[FEATURES]
    y = ml_data[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
    )

    evaluation_model = build_model()
    evaluation_model.fit(X_train, y_train)
    test_predictions = evaluation_model.predict(X_test)

    mae = mean_absolute_error(y_test, test_predictions)
    rmse = np.sqrt(
        mean_squared_error(y_test, test_predictions)
    )

    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("MAE", f"{mae:.3f} t/ha")
    metric2.metric("RMSE", f"{rmse:.3f} t/ha")

    if len(y_test) >= 2:
        score = r2_score(y_test, test_predictions)
        metric3.metric("R² Score", f"{score:.3f}")
    else:
        metric3.metric("R² Score", "Not available")

    st.caption(
        "Metrics are computed on a held-out test set. "
        "Small datasets can produce unstable or misleading scores."
    )

    # Train final model on all available rows
    final_model = build_model()
    final_model.fit(X, y)

    st.subheader("Predict crop yield")

    with st.form("yield_prediction_form"):
        col1, col2 = st.columns(2)

        with col1:
            pred_crop = st.selectbox(
                "Crop",
                sorted(ml_data["Crop"].unique()),
            )
            pred_state = st.selectbox(
                "State",
                sorted(ml_data["State"].unique()),
            )
            pred_year = st.number_input(
                "Year",
                min_value=int(ml_data["Year"].min()),
                max_value=int(ml_data["Year"].max()) + 10,
                value=int(ml_data["Year"].max()),
                step=1,
            )

        with col2:
            pred_area = st.number_input(
                "Cultivated area (hectares)",
                min_value=0.01,
                value=max(
                    0.01,
                    float(ml_data["Area_Hectares"].median()),
                ),
            )
            pred_rainfall = st.number_input(
                "Rainfall (mm)",
                min_value=0.0,
                value=max(
                    0.0,
                    float(ml_data["Rainfall_mm"].median()),
                ),
            )
            pred_fertilizer = st.number_input(
                "Fertilizer (kg/hectare)",
                min_value=0.0,
                value=max(
                    0.0,
                    float(
                        ml_data["Fertilizer_kg_per_hectare"].median()
                    ),
                ),
            )

        submitted = st.form_submit_button("Predict Crop Yield")

    if submitted:
        input_data = pd.DataFrame(
            [{
                "Year": pred_year,
                "State": pred_state,
                "Crop": pred_crop,
                "Area_Hectares": pred_area,
                "Rainfall_mm": pred_rainfall,
                "Fertilizer_kg_per_hectare": pred_fertilizer,
            }],
            columns=FEATURES,
        )

        prediction = float(final_model.predict(input_data)[0])

        st.success(
            f"Estimated crop yield: {prediction:.2f} tonnes/hectare"
        )
        st.caption(
            "This is a model estimate, not a guaranteed real-world yield. "
            "Verify with reliable agricultural data before practical use."
        )
