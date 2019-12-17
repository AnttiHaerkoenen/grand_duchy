import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Output, Input
import pandas as pd

from src.visualization.utils import make_kwic_table


kwic_data = pd.read_csv('../../data/processed/kwic_riksdag_storfurst.csv')
freg_data_abs = pd.read_csv('../../data/processed/frequencies_riksdag_all_abs.csv')
freq_data = pd.read_csv('../../data/processed/frequencies_riksdag_all.csv')

app = dash.Dash(__name__)

options = [{'label': k, 'value': k} for k in set(kwic_data['keyword'])]

app.layout = html.Div(children=[
    html.H2(children='Keyword'),

    html.Div([
        dcc.Dropdown(
            id='keyword-picker',
            options=options,
            value=options[0]['value'],
        ),

        dcc.RadioItems(
            id='abs-picker',
            options=[{'label': i.capitalize(), 'value': i} for i in ['absolute', 'relative']],
            value='absolute',
        ),
    ]),

    html.H2(children='Frequency'),

    dcc.Graph(id='bar-plot'),

    html.H2(children='Keywords in context'),

    dash_table.DataTable(id='kwic-table'),
])


@app.callback(
    Output('bar-plot', 'figure'),
    [Input('keyword-picker', 'value')]
)
def update_graph(keyword):
    return {
        'data': []
    }


@app.callback(
    Output('kwic-table', 'children'),
    [Input('keyword-picker', 'value'),
     Input('bar-plot', 'selectedData')]
)
def update_table(keyword, selection):
    year = selection
    data = kwic_data[(kwic_data['keyword'] == keyword) & (kwic_data['year'] == year)]
    return {}


if __name__ == '__main__':
    app.run_server(debug=True)
