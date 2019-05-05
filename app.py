# Import all neccessary libraries
import base64
import io
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

######################################################################

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div([
    # Setting headers
    html.H1(children='Kyphosis Angle Over Time'),
    # html.Div(children='''
    # Made by Jan Zajac.'''),

    # Formatting box for uploading of datafile
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '98%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'), # IMPORTANT !!!
])

######################################################################

# Function for reading in datafile uploaded and plotting graph
def parse_contents(contents, filename, value):
    content_type, content_string = contents.split(',')

    # function that determines sitting/standing based on force values. If force = -1 that means no force detecting = sitting
    def sitting(row):
        if row['force'] == -1:
            return 'Sitting'
        else:
            return 'Standing'

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            data = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
            data = data.drop([0], axis=0)

            # converting time column to a datatime type object
            data['time'] = pd.to_datetime(data['time'])

            # creating a boolean sitting column based on values in the 'force' column
            data['sitting'] = data.apply(lambda row: sitting(row), axis=1)

            # calculating a moving average of the kyphosis angle (window = 10) ie 1 minutes if data is collected every 5s
            data['ma'] = data.difference.rolling(window=50).mean()

            # setting rows to be picked out every half a minute to smoothen out dataset
            data = data.iloc[::6, :]

        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            data = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        dcc.Graph(
            id='example-graph',
            style={"height": "100vh"},
            figure={
                'data': [
                    {'x': data.time, 'y': data.ma, 'type': 'scatter', 'name': 'Kyphosis angle'},
                    {'x': data.time, 'y': data.sitting, 'type': 'scatter', 'name': 'Sitting/Standing', 'yaxis': 'y2'},
                ],
                'layout': {
                    'title': 'Patient Kyphosis Angle Over Time',
                    'yaxis': dict(title='Kyphosis Angle (°)',
                                  family = 'Courier New, monospace'),
                    'yaxis2': dict(title='Sitting/Standing?',
                       overlaying='y',
                       side='right'),
                    'legend': dict(orientation = "h"),
                    'xaxis': dict(title='Time',
                                  family = 'Courier New, monospace',
                                  autorange=True,
                                  rangeselector=dict(
                                      buttons=list([
                                          dict(count=10,
                                               label='10 min ',
                                               step='minute',
                                               stepmode='backward'),
                                          dict(count=1,
                                               label='Hour ',
                                               step='hour',
                                               stepmode='backward'),
                                          dict(step='all')
                                      ])
                                  ),
                                  rangeslider=dict(
                                      visible=True
                                  ),
                                  type='date'
                                  )
                }
            }
        )
    ])

######################################################################

# Update with new file if desired
@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


if __name__ == '__main__':
    app.run_server()
