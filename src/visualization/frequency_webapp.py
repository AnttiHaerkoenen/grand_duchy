import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import pandas as pd

from src.visualization.utils import make_kwic_table


data = pd.read_csv('../../data/processed/kwic_riksdag_storfurst.csv')

app = dash.Dash(__name__)

options = [{'label': k, 'value': k} for k in set(data['keyword'])]

app.layout = html.Div(children=[
    html.H2(children='Keyword'),

    dcc.Dropdown(
        id='keyword-picker',
        options=options,
        value=options[0]['value'],
    ),

    html.H2(children='Frequency'),

    dcc.Graph(id='bar-plot'),

    html.H2(children='Keywords in context'),

    html.Table(id='kwic-table'),
])


@app.callback(
    Output('bar-plot', 'figure'),
    [Input('keyword-picker', 'value')]
)
def update_graph():
    pass


@app.callback(
    Output('kwic-table', 'children'),
    [Input('keyword-picker', 'value'),
     Input('bar-plot', 'selectedData')]
)
def update_table():
    pass


if __name__ == '__main__':
    app.run_server(debug=True)
