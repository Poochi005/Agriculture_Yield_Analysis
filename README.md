# Agriculture Yield Analysis

A ready-to-run beginner-friendly project for exploring crop yield data in VS Code using Python, Pandas, Streamlit, and Plotly.

## Features
- Interactive filters for crop, state, and year
- KPI cards for total production, average yield, and cultivated area
- Crop-wise yield and year-wise production charts
- Rainfall and fertilizer analysis
- CSV upload support
- Download filtered data

## Run in VS Code (Windows)
1. Install Python 3.10+ and VS Code.
2. Open this folder in VS Code.
3. Open Terminal > New Terminal.
4. Create and activate a virtual environment:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   If activation is blocked, use `Set-ExecutionPolicy -Scope Process Bypass` in that terminal, then activate again.
5. Install packages:
   ```powershell
   python -m pip install -r requirements.txt
   ```
6. Run:
   ```powershell
   python -m streamlit run app.py
   ```
7. The app opens in your browser, usually at http://localhost:8501.

## Dataset
`data/agriculture_yield.csv` is a small **sample/demo dataset** created for this project. Replace it with verified data before presenting findings as real-world conclusions.

CSV columns:
- `Year`
- `State`
- `Crop`
- `Area_Hectares`
- `Production_Tonnes`
- `Rainfall_mm`
- `Fertilizer_kg_per_hectare`
- `Yield_Tonnes_per_Hectare`

For real data, use official government/open datasets and record the source, download date, and any cleaning steps.

## Power BI
You can import `data/agriculture_yield.csv` into Power BI Desktop (Get Data > Text/CSV) to create a Power BI report. This VS Code app is a companion dashboard; it is not a `.pbix` file.
