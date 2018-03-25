# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import datetime
from colour import Color

app = dash.Dash()

# Variables
text_style = dict(color='#444', fontFamily='sans-serif', fontWeight=300)
colors = list(Color('#68ff68').range_to(Color('#ff6868'),14))
           
# Import data and adjust entero count                    
df = pd.read_csv('https://raw.githubusercontent.com/ilyakats/'
                 'CUNY-DATA608/master/hw4/'
                 'riverkeeper_data_2013.csv', 
                 parse_dates=['Date'])
df['EnteroNo'] = df['EnteroCount']
df['EnteroNo'] = df['EnteroCount'].map(lambda x: x.lstrip('<>')).astype(int)

# Format output table
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
                    style['background'] = '#8B4513'
                    style['color'] = '#FFFFFF'
                else:
                    style['background'] = '#32FF32'
            if col=='Days Since Last Check':
                if value>14:
                    style['background'] = colors[13].hex
                else:
                    style['background'] = colors[value-1].hex
            if col=='':
                if value:
                    image = 'boat_small.png'
                else:
                    image = 'poop_small.png'
                value = html.Img(src='https://raw.githubusercontent.com/ilyakats/'
                                 'CUNY-DATA608/master/hw4/'+image, 
                                 style={'width':'20', 'height':'20'})
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
            html.H2('Latest Enterococcus Counts for Hudson River Estuary Sites', 
                    style=text_style),

            html.P('This page lets you evaluate and compare possible launch sites. '
                   'Please note that there are multiple factors that determine '
                   'public health risk. This page examines exposure to fecal '
                   'contamination. Enterococcus ("Entero") is a fecal indicating '
                   'bacteria that lives in the intestines of humans and other '
                   'warm-blooded animals. EPA recommends public notification '
                   'and possible temporary beach closure for single Entero '
                   'sample above 60 cells/100 mL. Samples testing above this '
                   'threshold appear in brown on this site, while those below '
                   'it appear in green. Addtionally, the closer the launch date '
                   'is to the water quality measurement date, the more '
                   'confident you can be about the results. Days since last '
                   'check are highlighted from green to red depending on how '
                   'recent the check was (anything over two weeks is red).', 
                   style=text_style),
            html.P('Next version of this page will include ability to '
                   'map all sites and to compare '
                   'measurements taken on multiple dates for a single site '
                   '(using geometric mean, for example). '
                   'For now more information is available at the Riverkeeper '
                   'website (http://www.riverkeeper.org).', 
                   style=text_style),
            html.P('The slider below lets you pick a launch date based on '
                     'available data (2006 through 2013).', 
                     style=text_style),
            html.Label('Pick a date:', style=text_style),
            html.Div([
                    dcc.Slider(
                            id='date-slider',
                            min=0, max=2922, value=365,
                            marks={
                                    0: {'label': ''},
                                    365: {'label': '2007', 'style': text_style},
                                    730: {'label': '2008', 'style': text_style},
                                    1096: {'label': '2009', 'style': text_style},
                                    1461: {'label': '2010', 'style': text_style},
                                    1826: {'label': '2011', 'style': text_style},
                                    2191: {'label': '2012', 'style': text_style},
                                    2557: {'label': '2013', 'style': text_style},
                                    2922: {'label': ''}
                                    },
                            included=False
                            )],
                    style={
                            'backgroundColor': 'rgb(250, 250, 250)',
                            'padding': '10px 5px 20px 5px'
                            }),
            html.Label('Sort by:', style=text_style),
            dcc.RadioItems(
                id='sort-buttons',
                options=[{'label': i, 'value': i} for i in ['Site', 'Entero Count']],
                value='Site',
                labelStyle={**text_style, 'display': 'inline-block'}
            )
            ],
    style={
            'borderBottom': 'thin lightgrey solid',
            'backgroundColor': 'rgb(250, 250, 250)',
            'padding': '10px 5px 20px 5px'
            }),
    html.Div(id='selected-date', style={**text_style, 'padding': '10px'}),
    html.Div(id='output-date-slider')
])

@app.callback(
        dash.dependencies.Output('selected-date', 'children'),
        [dash.dependencies.Input('date-slider', 'value')])
def update_date(value):
    return 'Selected Date: {}'.format((datetime.datetime(2006, 1, 1, 0, 0) + 
            datetime.timedelta(days=value)).strftime('%m/%d/%Y'))

@app.callback(
        dash.dependencies.Output('output-date-slider', 'children'),
        [dash.dependencies.Input('date-slider', 'value'),
         dash.dependencies.Input('sort-buttons', 'value')])
def update_output(value, sortcol):
    d = datetime.datetime(2006, 1, 1, 0, 0) + datetime.timedelta(days=value)
    cur_df = df[df['Date']<d]
    idx = cur_df.groupby(['Site'])['Date'].transform(max) == cur_df['Date']
    latest_df = cur_df[idx][['Site','Date','EnteroNo']]
    latest_df.columns = ['Site', 'Date', 'Entero Count']
    latest_df['DaysSince'] = (d-latest_df['Date']).dt.days
    latest_df['Date'] = latest_df['Date'].dt.strftime('%m/%d/%Y')
    latest_df['Status'] = latest_df['Entero Count']<61
    latest_df = latest_df[['Status', 'Site', 'Entero Count', 'Date', 'DaysSince']]
    latest_df.columns = ['', 'Site', 'Entero Count', 'Date of Last Check', 
                         'Days Since Last Check']
    latest_df = latest_df.sort_values(sortcol)
    return generate_table(latest_df)

if __name__ == '__main__':
    app.run_server(debug=False)