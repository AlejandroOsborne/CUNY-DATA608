# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import datetime
import numpy as np

app = dash.Dash()
server = app.server

# Variables
text_style = dict(color='#444', fontFamily='sans-serif', fontWeight=300)
           
# Import data and adjust entero count                    
df = pd.read_csv('https://raw.githubusercontent.com/ilyakats/'
                 'CUNY-DATA608/master/hw4/'
                 'riverkeeper_data_2013.csv', 
                 parse_dates=['Date'])
df['EnteroNo'] = df['EnteroCount']
df['EnteroNo'] = df['EnteroCount'].map(lambda x: x.lstrip('<>')).astype(int)
sites = df['Site'].sort_values().unique()

# Format output table
def generate_table(dataframe):
    rows = []
    for i in range(len(dataframe)):
        row = []
        for col in dataframe.columns:
            value = dataframe.iloc[i][col]
            style = {'textAlign':'Center'}
            row.append(html.Td(value, style=style))
        if i % 2 == 0:
            style = {'background':'#EEEEEE'}
        else:
            style = {'background':'#FFFFFF'}
        rows.append(html.Tr(row, style=style))
    return html.Table(
        [html.Tr([html.Th(col) for col in dataframe.columns])] +
        rows, style={**text_style, 'width':'100%'}
    )

app.layout = html.Div(children=[
    html.Div([
            html.H2('Enterococcus Counts vs Rain Totals (Hudson River Estuary)', 
                    style=text_style),

            html.P('This page lets you compare enterococcus readings against '
                   'four day rain total at a given site. Enterococcus '
                   '("Entero") is a fecal indicating bacteria that lives '
                   'in the intestines of humans and other warm-blooded animals. '
                   'Please note that entero counts have been transformed using '
                   'natural logarithm. The first plot shows both readings over '
                   'time. The second plot shows relationship between rain total '
                   'and corresponding entero counts. The area that falls below '
                   'the EPA\'s recommended site closure level (60 cells/100 mL) is '
                   'highlighted in green on both plots. Pearson correlation '
                   'coefficient is also presented (additional statistical '
                   'analysis can be added in future updates).', 
                   style=text_style),
            html.P('More information is available at the Riverkeeper '
                   'website (http://www.riverkeeper.org). '
                   'Data is courtesy of the site.', 
                   style=text_style),
            html.P('', 
                     style=text_style),
            html.Label('Pick a site:', style=text_style),
            html.Div([
                    dcc.Dropdown(
                            id='site-picker',
                            options=[{'label': i, 'value': i} for i in sites],
                            value='125th St. Pier'
                            )
                    ],style=text_style)
            ],
    style={
            'borderBottom': 'thin lightgrey solid',
            'backgroundColor': 'rgb(250, 250, 250)',
            'padding': '10px 5px 20px 5px'
            }),
    dcc.Graph(id='output-plot1'),
    dcc.Graph(id='output-plot2'),
    html.Div(id='coef', style={**text_style, 'padding': '10px', 
                               'font-weight': 'bold',
                               'backgroundColor': '#8CB4FF'}),
    html.Div(id='output-table', style={'padding': '20px'})
])

@app.callback(
        dash.dependencies.Output('output-plot1', 'figure'),
        [dash.dependencies.Input('site-picker', 'value')])
def update_graph1(site):
    cur_df = df[df['Site']==site].sort_values('Date')
    ytop = 0.2+max(np.log(cur_df['EnteroNo'].max()),cur_df['FourDayRainTotal'].max())
    trace1 = go.Scatter(
            x=cur_df['Date'], y=np.log(cur_df['EnteroNo']),
            text='Estero Count: '+cur_df['EnteroNo'].astype(str),
            mode='lines+markers',
            marker={
                'size': 10,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name='Entero Count')
    trace2 = go.Scatter(
            x=cur_df['Date'], y=cur_df['FourDayRainTotal'],
            mode='lines+markers',
            marker={
                'size': 10,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name='Rain Total',
            yaxis='y2')
    layout = go.Layout(
                shapes = [{
                        'type': 'rect',
                        'xref': 'paper', 'yref': 'y',
                        'x0': 0, 'y0': 0,
                        'x1': 1, 'y1': np.log(60),
                        'fillcolor': '#00FF00',
                        'opacity': 0.1,
                        'line': {'width': 0}
                        }],
                title=site+': Entero Count+Rain Total Time Series',
                xaxis={'title': ''},
                yaxis={'title': 'Log of Entero Count',
                       'range': [0,ytop]},
                yaxis2={'title': '4 Day Rain Total',
                       'range': [0,ytop],
                        'overlaying': 'y',
                        'side': 'right'},
                margin={'l': 40, 'b': 40, 't': 80, 'r': 0},
                hovermode='closest')
    return {'data': [trace1, trace2],
            'layout': layout}
    
@app.callback(
        dash.dependencies.Output('output-plot2', 'figure'),
        [dash.dependencies.Input('site-picker', 'value')])
def update_graph2(site):
    cur_df = df[df['Site']==site].sort_values('Date')
    data = go.Scatter(
            x=cur_df['FourDayRainTotal'], y=np.log(cur_df['EnteroNo']),
            text='Estero Count: '+cur_df['EnteroNo'].astype(str),
            mode='markers',
            marker={
                'size': 10,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name='Entero Count')
    layout = go.Layout(
                shapes = [{
                        'type': 'rect',
                        'xref': 'paper', 'yref': 'y',
                        'x0': 0, 'y0': 0,
                        'x1': 1, 'y1': np.log(60),
                        'fillcolor': '#00FF00',
                        'opacity': 0.1,
                        'line': {'width': 0}
                        }],
                title=site+': Entero Count vs Rain Total',
                xaxis={'title': '4 Day Rain Total'},
                yaxis={'title': 'Log of Entero Count'},
                margin={'l': 40, 'b': 80, 't': 80, 'r': 0},
                hovermode='closest')
    return {'data': [data],
            'layout': layout}

@app.callback(
        dash.dependencies.Output('coef', 'children'),
        [dash.dependencies.Input('site-picker', 'value')])
def update_coef(value):
    cur_df = df[df['Site']==value].sort_values('Date')
    pcc = np.corrcoef(cur_df['FourDayRainTotal'],np.log(cur_df['EnteroNo']))[0,1]
    return 'Pearson Correlation Coefficient (4 Day Rain Total vs Log of Entero Count): {:0.2f}'.format(pcc)

@app.callback(
        dash.dependencies.Output('output-table', 'children'),
        [dash.dependencies.Input('site-picker', 'value')])
def update_output(value):
    cur_df = df[df['Site']==value]
    cur_df = cur_df[['Date', 'EnteroNo', 'FourDayRainTotal']]
    cur_df.columns = ['Date', 'Entero Count', '4 Day Rain Total']
    cur_df = cur_df.sort_values('Date')
    return generate_table(cur_df)

if __name__ == '__main__':
    app.run_server(debug=False)