from pathlib import Path

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Output, Input
import pandas as pd

data_dir = Path('../../data/processed')

freq_lemma_data = pd.read_csv(data_dir / 'frequencies_FI_newspapers_lemma.csv')
freg_lemma_data_abs = pd.read_csv(data_dir / 'frequencies_FI_newspapers_lemma_abs.csv')
freq_regex_data = pd.read_csv(data_dir / 'frequencies_FI_newspapers_regex.csv')
freg_regex_data_abs = pd.read_csv(data_dir / 'frequencies_FI_newspapers_regex_abs.csv')

keywords = set(freq_lemma_data.columns) - {'year', 'Unnamed: 0'}

app = dash.Dash(__name__)
app.title = "Sanomalehdet"

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
            options=[
                {'label': i.capitalize(), 'value': i}
                for i in ['absolute', 'relative']
            ],
            value='absolute',
            labelStyle={'display': 'inline-block'}
        ),
    ]),

    html.H2(children='Lemma'),
    html.Div([
        dcc.RadioItems(
            id='lemma-picker',
            options=[
                {'label': i.capitalize(), 'value': i}
                for i in ['lemma', 'regex']
            ],
            value='regex',
            labelStyle={'display': 'inline-block'}
        ),
    ]),

    dcc.Graph(id='bar-plot'),
])


@app.callback(
    Output('bar-plot', 'figure'),
    [Input('keyword-picker', 'value'),
     Input('abs-picker', 'value'),
     Input('lemma-picker', 'value')]
)
def update_graph(
        keyword,
        abs_or_rel,
        lemma_or_regex,
):
    if abs_or_rel == 'absolute' and lemma_or_regex == 'lemma':
        data = freg_lemma_data_abs
    elif abs_or_rel == 'relative' and lemma_or_regex == 'lemma':
        data = freq_lemma_data
    elif abs_or_rel == 'absolute' and lemma_or_regex == 'regex':
        data = freg_regex_data_abs
    else:
        data = freq_regex_data

    x = data.index
    y = data[keyword]

    return {
        'data': [{
            'x': x,
            'y': y,
            'type': 'bar',
            'name': keyword,
        }]
    }


if __name__ == '__main__':
    app.run_server(debug=True)
