# The base app if you were making everything one piece at a time

from shiny import App, ui, reactive, render
import pandas as pd
from palmerpenguins import load_penguins

penguins = (
    load_penguins()
    .dropna()
    .loc[:, ["species", "bill_length_mm", "body_mass_g"]]
)

app_ui = ui.page_sidebar(
    ui.sidebar(
        # Species checkbox group
        ui.input_checkbox_group(
            "filter_species",
            "Select species",
            choices=sorted(penguins["species"].unique()),
            selected=sorted(penguins["species"].unique()),
        ),
        # Bill length slider
        ui.input_slider(
            "filter_bill_length_mm",
            "Range for bill_length_mm",
            min=float(penguins["bill_length_mm"].min()),
            max=float(penguins["bill_length_mm"].max()),
            value=[
                float(penguins["bill_length_mm"].min()),
                float(penguins["bill_length_mm"].max()),
            ],
            step=1,
        ),
        # Body mass slider
        ui.input_slider(
            "filter_body_mass_g",
            "Range for body_mass_g",
            min=float(penguins["body_mass_g"].min()),
            max=float(penguins["body_mass_g"].max()),
            value=[
                float(penguins["body_mass_g"].min()),
                float(penguins["body_mass_g"].max()),
            ],
            step=1,
        ),
    ),
    ui.card(
        ui.card_header("Filtered Penguins Data"),
        ui.output_data_frame("filtered_data"),
    ),
)


# Define the server logic
def server(input, output, session):
    @reactive.calc
    def get_filtered_data():
        # Start with all rows
        mask = pd.Series(True, index=penguins.index)

        # Apply filters for each column
        for col in penguins.columns:
            if pd.api.types.is_numeric_dtype(penguins[col]):
                # Handle numeric filters
                min_val, max_val = getattr(input, f"filter_{col}")()
                mask = (
                    mask
                    & (penguins[col] >= min_val)
                    & (penguins[col] <= max_val)
                )
            else:
                # Handle categorical filters
                selected_categories = getattr(input, f"filter_{col}")()
                mask = mask & penguins[col].isin(selected_categories)

        # Return the filtered data
        return penguins[mask].copy()

    @output
    @render.data_frame
    def filtered_data():
        return get_filtered_data()


# Create and return the app
app = App(app_ui, server)
