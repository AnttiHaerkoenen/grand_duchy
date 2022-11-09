import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd


def make_kwic_table(
        data: pd.DataFrame,
        max_rows: int = 10,
):
    return html.Table(
        [html.Tr([html.Th(col) for col in data.columns])] +
        [html.Tr([
            html.Td(data.iloc[i][col]) for col in data.columns
        ]) for i in range(min(len(data), max_rows))]
    )

if __name__ == "__main__":
    pass
