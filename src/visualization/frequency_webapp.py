from pathlib import Path

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Output, Input
import pandas as pd

data_dir = Path('../../data/processed')

freg_data_abs = pd.read_csv(data_dir / 'frequencies_riksdag_all_abs.csv')
freq_data = pd.read_csv(data_dir / 'frequencies_riksdag_all.csv', encoding='utf-8')

keywords = set(freq_data.columns) - {'year', 'Unnamed: 0'}

app = dash.Dash(__name__)
app.title = "Riksdag"

server = app.server

options = [{'label': k, 'value': k} for k in keywords]

app.layout = html.Div(children=[
    html.H2(children='Keyword'),

    html.Div([
        dcc.Dropdown(
            id='keyword-picker',
            options=options,
            value=options[0]['value'],
        ),
    ]),

    html.H2(children='Frequency'),
    html.Div([
        dcc.RadioItems(
            id='abs-picker',
            options=[{'label': i.capitalize(), 'value': i} for i in ['absolute', 'relative']],
            value='absolute',
            labelStyle={'display': 'inline-block'}
        ),
    ]),

    dcc.Graph(id='bar-plot'),

    html.H2(children='Keywords in context'),

    dash_table.DataTable(
        id='kwic-table',
        columns=[
            {'name': col.capitalize(), 'id': col} for col in ['context', 'file']
        ],
        style_data={
            'whiteSpace': 'normal',
            'height': 'auto',
            'text-align': 'left',
        },
        style_header={
            'text-align': 'left',
        }
    ),
])


@app.callback(
    Output('bar-plot', 'figure'),
    [Input('keyword-picker', 'value'),
     Input('abs-picker', 'value')]
)
def update_graph(
        keyword,
        abs_or_rel,
):
    if abs_or_rel == 'absolute':
        data = freg_data_abs
    else:
        data = freq_data

    x = data['year']
    y = data[keyword]

    return {
        'data': [{
            'x': x,
            'y': y,
            'type': 'bar',
            'name': keyword,
        }]
    }


@app.callback(
    Output('kwic-table', 'data'),
    [Input('keyword-picker', 'value'),
     Input('bar-plot', 'selectedData')]
)
def update_table(
        keyword,
        selection,
):
    if selection is None:
        points = []
    else:
        points = selection.get('points', [])

    years = [point['x'] for point in points]
    data = pd.read_csv(data_dir / f'kwic_riksdag_{keyword}.csv')

    if 0 < len(years):
        data = data[data['year'].isin(years)]

    return data.to_dict('records')


if __name__ == '__main__':
    app.run_server(debug=True)
