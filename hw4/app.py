# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

app = dash.Dash()

df = pd.read_csv('riverkeeper_data_2013', parse_dates=['Date'])

df['Date']=df['Date'].dt.strftime('%Y-%m-%d')

app.layout = html.Div(children=[
    html.H1(children='Hello 678'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),
    html.Div([
            html.Label('Pick a date:'),
            dcc.Slider(
                    id='date-slider',
                    min=0, max=365, value=25,
                    marks={
                            0: {'label': 'Jan-2018'},
                            196: {'label': 'Jun-2018'},
                            365: {'label': 'Dec-2018'}
                            },
                    included=False
                    ),
            html.Div(id='output-date-slider')
            ],
    style={
            'borderBottom': 'thin lightgrey solid',
            'backgroundColor': 'rgb(250, 250, 250)',
            'padding': '10px 5px 20px 5px'
            }),
    
    html.Div([
    html.Label('Plot'),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }
    )])
])
    
@app.callback(
        dash.dependencies.Output('output-date-slider', 'children'),
        [dash.dependencies.Input('date-slider', 'value')])

def update_output(value):
    return 'You have selected "{}"'.format(value)


if __name__ == '__main__':
    app.run_server(debug=True)