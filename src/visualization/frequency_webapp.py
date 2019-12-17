import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Output, Input
import pandas as pd

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
    data = kwic_data[(kwic_data['keyword'] == keyword)]

    if 0 < len(years):
        data = data[data['year'].isin(years)]

    return data.to_dict('records')


if __name__ == '__main__':
    app.run_server(debug=True)
