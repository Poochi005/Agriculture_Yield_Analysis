# Power BI quick guide

1. Open Power BI Desktop.
2. Select **Get data > Text/CSV**.
3. Choose `data/agriculture_yield.csv` and select **Load**.
4. Add visuals:
   - Card: Sum of `Production_Tonnes`
   - Card: Average of `Yield_Tonnes_per_Hectare`
   - Clustered column chart: `Crop` vs average `Yield_Tonnes_per_Hectare`
   - Line chart: `Year` vs sum of `Production_Tonnes`
   - Scatter chart: `Rainfall_mm` vs `Yield_Tonnes_per_Hectare`
   - Slicers: `Year`, `State`, `Crop`
5. Add a note on the report page that the bundled data is illustrative sample data. Replace it with an official dataset before presenting real-world conclusions.
