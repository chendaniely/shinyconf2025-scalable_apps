# in-app module

from shiny import App, ui, reactive, render, module
import pandas as pd
from palmerpenguins import load_penguins


def create_ui_filters(df, columns):
    ui_filters = {}

    for col in columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            min_val = float(df[col].min())
            max_val = float(df[col].max())
            ui_filters[col] = {
                "filter_method": "sliders2_between",
                "component": ui.input_slider(
                    f"filter_{col}",
                    f"Range for {col}",
                    min=min_val,
                    max=max_val,
                    value=[min_val, max_val],
                    step=1,
                ),
            }

        else:
            unique = sorted(df[col].unique())
            ui_filters[col] = {
                "filter_method": "list_isin",
                "component": ui.input_checkbox_group(
                    f"filter_{col}",
                    f"Select {col}",
                    choices=unique,
                    selected=unique,
                ),
            }

    # print(ui_filters)
    return ui_filters


@module.ui
def filter_ui():
    return ui.output_ui("df_filters")


@module.server
def filter_server(input, output, session, ui_filters, df, columns):
    @render.ui
    def df_filters():
        return [(ui_filters[col]["component"]) for col in columns]

    @reactive.calc
    def get_filtered_data():
        mask = pd.Series(True, index=df.index)

        for col in columns:
            if ui_filters[col]["filter_method"] == "sliders2_between":
                min_val, max_val = getattr(input, f"filter_{col}")()
                mask = mask & df[col].between(min_val, max_val)
            elif ui_filters[col]["filter_method"] == "list_isin":
                selected_categories = getattr(input, f"filter_{col}")()
                mask = mask & df[col].isin(selected_categories)
            else:
                raise ValueError

        return df[mask]

    return {
        "df": get_filtered_data,
    }


penguins = (
    load_penguins()
    .dropna()
    .loc[:, ["species", "bill_length_mm", "body_mass_g"]]
)

ui_filters = create_ui_filters(penguins, penguins.columns)

app_ui = ui.page_sidebar(
    ui.sidebar(filter_ui("filters")),
    ui.card(
        ui.card_header("Filtered Penguins Data"),
        ui.output_data_frame("filtered_data"),
    ),
)


# Define the server logic
def server(input, output, session):
    @render.data_frame
    def filtered_data():
        return my_module["df"]()

    my_module = filter_server(
        "filters",
        ui_filters=ui_filters,
        df=penguins,
        columns=penguins.columns,
    )


# Create and return the app
app = App(app_ui, server)
