# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import pandas as pd
import datetime

app = dash.Dash()

app.scripts.config.serve_locally=True

df = pd.read_csv('https://raw.githubusercontent.com/ilyakats/'
                 'CUNY-DATA608/master/hw4/'
                 'riverkeeper_data_2013.csv', 
                 parse_dates=['Date'])

df['EnteroNo'] = df['EnteroCount']
df['EnteroNo'] = df['EnteroCount'].map(lambda x: x.lstrip('<>')).astype(int)

# df['Date']=df['Date'].dt.strftime('%Y-%m-%d')

# max_days = (df['Date'].max()-df['Date'].min()).days

#cur_df = df[df['Date']<d]
#idx = cur_df.groupby(['Site'])['Date'].transform(max) == cur_df['Date']
#latest_df = cur_df[idx]

def generate_table(dataframe):
    rows = []
    for i in range(len(dataframe)):
        row = []
        for col in dataframe.columns:
            value = dataframe.iloc[i][col]
            if col=='Site':
                style = {'textAlign':'Left'}
            else:
                style = {'textAlign':'Center'}
            if col=='Entero Count':
                if value>60:
                    style['background'] = '#FC3232'
                    style['text'] = '#FFFFFF'
                else:
                    style['background'] = '#32FF32'
            row.append(html.Td(value, style=style))
        rows.append(html.Tr(row))
    return html.Table(
        [html.Tr([html.Th(col) for col in dataframe.columns])] +
        rows
    )

app.layout = html.Div(children=[
    html.H1(children='Hello 678'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),
    html.Div([
            html.Label('Pick a date:'),
            dcc.Slider(
                    id='date-slider',
                    min=0, max=2922, value=365,
                    marks={
                            0: {'label': ''},
                            365: {'label': '2007'},
                            730: {'label': '2008'},
                            1096: {'label': '2009'},
                            1461: {'label': '2010'},
                            1826: {'label': '2011'},
                            2191: {'label': '2012'},
                            2557: {'label': '2013'},
                            2922: {'label': ''}
                            },
                    included=False
                    )
            ],
    style={
            'borderBottom': 'thin lightgrey solid',
            'backgroundColor': 'rgb(250, 250, 250)',
            'padding': '10px 5px 20px 5px'
            }),
    html.Div(id='output-date-slider')
])
    
    
#@app.callback(
#        dash.dependencies.Output('output-date-slider', 'rows'), 
#        [dash.dependencies.Input('date-slider', 'value')])

#def update_rows(value):
#    d = datetime.datetime(2006, 1, 1, 0, 0) + datetime.timedelta(days=value)
#    cur_df = df[df['Date']<d]
#    idx = cur_df.groupby(['Site'])['Date'].transform(max) == cur_df['Date']
#    latest_df = cur_df[idx]
#    return latest_df.to_dict('records')


@app.callback(
        dash.dependencies.Output('output-date-slider', 'children'),
        [dash.dependencies.Input('date-slider', 'value')])

def update_output(value):
    d = datetime.datetime(2006, 1, 1, 0, 0) + datetime.timedelta(days=value)
    cur_df = df[df['Date']<d]
    idx = cur_df.groupby(['Site'])['Date'].transform(max) == cur_df['Date']
    latest_df = cur_df[idx][['Site','Date','EnteroNo','SampleCount']]
    latest_df.columns = ['Site', 'Date', 'Entero Count', 'No of Samples']
    latest_df['Date'] = latest_df['Date'].dt.strftime('%m/%d/%Y')
    return generate_table(latest_df)


if __name__ == '__main__':
    app.run_server(debug=True)