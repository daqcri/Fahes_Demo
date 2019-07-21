import base64
import datetime
import io
import os 
from os import listdir
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import ntpath
import csv
import json
import pandas as pd
from fahes_caller import executeFahes
from components import Header, make_dash_table, get_menu
import plotly.graph_objs as go

DATA_FOLDER = "./data"


# important link https://dash.plot.ly/datatable/interactivity
# external CSS stylesheets
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]



app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions']=True
app.title = 'FAHES'

DATA_FOLDER = "./data"
gdf = None
gresults = None
param_dict = dict()
param_dict["results_main_dir"] = "../Results/"




def read_table(tab_name):
    t_name = ntpath.basename(tab_name)
    try:
        df = pd.read_csv(filepath_or_buffer=tab_name, dtype=object, delimiter=',', low_memory=False,
                         quoting=csv.QUOTE_ALL, doublequote=True)
    except ValueError:
        try:
            df = pd.read_csv(filepath_or_buffer=tab_name, dtype=object, delimiter=',', low_memory=False,
                             quoting=csv.QUOTE_ALL, doublequote=True, encoding="ISO-8859-1")
        except:
            print("Error reading csv file .. file encoding is not recognizable")
            return None
    return df

def get_csv_files(folder):
    csv_files = []
    folder_contents = listdir(folder)
    for item in folder_contents:
        if item.endswith('.csv'):
            csv_files.append(item)
    return csv_files
def is_non_zero_file(fpath):  
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0

def dynamic_page():
    return html.Div([
        Header(),
        html.Div([    
            html.Div([
                dcc.Dropdown(
                        id='uploaded-datasets',
                        options=[{'label': i, 'value': i} for i in get_csv_files(DATA_FOLDER)],
                        placeholder='Select a Dataset',
                    )
                ],style={
                        'width': '220px',
                        'display': 'inline-block',
                        'margin-left': '25px',
                    } 
                
            ), 
            html.Div([
                dcc.Upload(
                    id='upload-data',
                    children = html.Div([
                        html.Button(' Browse ', className='fa fa-upload')
                    ],style={
                        'backgroundColor':'green',
                        'color':'white',
                        'margin-left': '5px',
                    }),
                    
                    multiple=False
                ),
            ]),
            html.Button('Run FAHES', className='fa', id='button', 
                style={
                        'backgroundColor':'green',
                        'color':'white',
                        'width': '200',
                        'flow':'right',
                        'margin-left': '15px',
                    }),
        ], className="row",
            style={
                'width': '100%',
                'height':'50px',
                'borderWidth': '1px',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin-left': '25px',
                'margin-top': '10px',
            }),
        html.Div(id='output-data-upload'),
        html.Div(id='output-data-dropdown',
            style={
                'width': '100%',
                'height': '440px',
                'borderWidth': '1px',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin-left': '50px',
                'margin-right': '25px',
                'overflowY': 'scroll',
            }),
        html.Hr(),  # horizontal line
        html.Div(id = 'output-results',
            style={
                'width': '100%',
                'height': '200px',
                'borderWidth': '1px',
                'borderRadius': '5px',
                'textAlign': 'left',
                'margin-left': '25px',
                'margin-right': '25px',
                'margin-top': '40px'
            }),
        # Footer()
    ], className='body')

app.layout = dynamic_page



def upload_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    new_file_name = ''
    try:
        if filename.endswith('csv'):
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
            if filename.endswith('xls'):
                new_file_name = filename.replace('.xls', '.csv')
            if filename.endswith('xlsx'):
                new_file_name = filename.replace('.xlsx', '.csv')
        filename2 = os.path.join(DATA_FOLDER, filename)
        df.to_csv(filename2, sep=',', encoding='latin', index=False, quoting=csv.QUOTE_ALL, doublequote=True)
    except Exception as e:
        print(e)
        return html.Div([
            ''
        ])
    return html.Div([
            ''
        ])


def parse_contents(filename):
    global gdf
    try:
        if filename.endswith('csv'):
            # Assume that the user uploaded a CSV file
            filename2 = os.path.join(DATA_FOLDER, filename)
            df = read_table(filename2)
            gdf = df
        # elif 'xls' in filename:
        #     # Assume that the user uploaded an excel file
        #     df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            css=[{
                'selector': '.dash-cell div.dash-cell-value',
                'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
            }],
            style_cell={
                'whiteSpace': 'no-wrap',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'maxWidth': 0,
                'textAlign':'left'
            },
            style_cell_conditional=[{
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }],
            style_header={
                'backgroundColor': 'white',
                'fontWeight': 'bold'
            },
            style_table={
                'max_rows_in_viewport':15,
                'maxHeight': '400px',
                'overflowY': 'scroll'
            },
            pagination_settings={
            "current_page": 0,
            "page_size": 50,
            },
        ),
        # html.Hr(),  # horizontal line
    ], className='ui-grid-resize-columns ui-grid-pagination')


@app.callback([Output('output-data-upload', 'children'),
                Output('uploaded-datasets', 'options'),
                Output('uploaded-datasets', 'value')],
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output_data(content, fname, modified):
    if content:
        grid = upload_contents(content, fname)
        options=[{'label': i, 'value': i} for i in get_csv_files(DATA_FOLDER)]
        value=fname
        return grid, options, value
    else:
        options=[{'label': i, 'value': i} for i in get_csv_files(DATA_FOLDER)]
        return html.Div(['']), options, ''


@app.callback(Output('output-data-dropdown', 'children'),
              [Input('uploaded-datasets', 'value')])
def output_dropdown(fname):
    options=[{'label': i, 'value': i} for i in get_csv_files(DATA_FOLDER)]
    if fname:
        grid = parse_contents(fname)
        return grid
    else:
        return html.Div([''])
        
@app.callback(
    Output('output-results', 'children'),
    [Input('button', 'n_clicks')],
    [State('uploaded-datasets', 'value')])
def update_output_discovery(n_clicks, fname):
    
    global gresults

    if fname:
        tab_name = os.path.join(DATA_FOLDER, fname)
        dmvs_table_name = executeFahes(tab_name)
        if not(is_non_zero_file(dmvs_table_name)):
            return html.Div(['No DMVs Found'])
        with open (dmvs_table_name) as json_file:
            gresults = json.load(json_file)
        if len(gresults) > 0:
        
            return html.Div([
                dcc.Tabs(
                    id="tabs-with-classes",
                    value='fahes',
                    parent_className='custom-tabs',
                    className='tab',
                    children=[
                        dcc.Tab(
                            label='FAHES',
                            value='fahes',
                            className='custom-tab',
                            selected_className='custom-tab--selected'
                        ),
                        dcc.Tab(
                            label='Syntactic Outliers',
                            value='syn',
                            className='custom-tab',
                            selected_className='custom-tab--selected'
                        ),
                        dcc.Tab(
                            label='Numerical Outliers',
                            value='outliers', className='custom-tab',
                            selected_className='custom-tab--selected'
                        ),
                        dcc.Tab(
                            label='Random DMVs',
                            value='rand', className='custom-tab',
                            selected_className='custom-tab--selected'
                        ),
                    ]),
                html.Div(id='tabs-content-classes')
            ])        
        else:
            html.Div([''])
    else:
        html.Div(['The data file is missing'])
    if n_clicks:
        return html.Div(['Something goes wrong after {}'.format(n_clicks)])
    return html.Div([''])





@app.callback(Output('tabs-content-classes', 'children'),
              [Input('tabs-with-classes', 'value')],
              [State('uploaded-datasets', 'value')])
def render_content(tab, tab_name):
    global gdf, gresults
    
    if tab == 'fahes':
        # att_names = gdf.columns.tolist()
        if gresults:
            dmvs = gresults['DMVs']
            dmvs_list = []
            for ii in range(len(dmvs_list)):
                dmvs_list.remove(dmvs_list[0])
            for i in range(len(dmvs)):
                dmvs_list.append(dmvs[i]['DMV'][0:3])
            # print (dmvs_list)
            dmvs_df = pd.DataFrame(dmvs_list, columns = ['Attribute', 'Value', 'Frequency'])
            return html.Div([
                dash_table.DataTable(
                data=dmvs_df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in dmvs_df.columns],
                id='fahes-table',
                row_deletable=True,
                css=[{
                    'selector': '.dash-cell div.dash-cell-value',
                    'rule': 'display: inline; white-space: inherit; margin-left: 20px; overflow: inherit; text-overflow: inherit;'
                }],
                style_cell={
                    'whiteSpace': 'no-wrap',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'maxWidth': '500px',
                    'textAlign':'left',
                    'font-size': '150%',
                },
                style_cell_conditional=[{
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }],
                style_header={
                    'backgroundColor': 'white',
                    'fontWeight': 'bold'
                },
                style_table={
                    'max_rows_in_viewport':15,
                    'maxHeight': '400px',
                    'maxWidth':'800px',
                    'overflowY': 'scroll',
                    'margin-left': '20px',
                    # 'border': 'thin lightgrey solid',
                }
            ),
                # html.H3('Select an attribute to see the patterns extracted from the attribute.'),
                # html.Div(id='dmvs-container-hidden', className="six columns"), 
                html.Div(id='dmvs-container-hidden', style={'display':'none'}),
            ], className="row ")
        else:
            return html.Div([''])

    elif tab == 'syn':
        dmvs = gresults['DMVs']
        dmvs_list = []
        for ii in range(len(dmvs_list)):
            dmvs_list.remove(dmvs_list[0])
        for i in range(len(dmvs)):
            if 'SYN' in dmvs[i]['DMV'][3]:
                dmvs_list.append(dmvs[i]['DMV'][0:3])
        # print (dmvs_list)
        if len(dmvs_list) > 0:
            dmvs_df = pd.DataFrame(dmvs_list, columns = ['Attribute', 'Value', 'Frequency'])
            return html.Div([
                dash_table.DataTable(
                data=dmvs_df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in dmvs_df.columns],
                id='syn-table',
                row_selectable="single",
                # row_deletable=True,
                css=[{
                    'selector': '.dash-cell div.dash-cell-value',
                    'rule': 'display: inline; white-space: inherit; margin-left: 20px; overflow: inherit; text-overflow: inherit;'
                }],
                style_cell={
                    'whiteSpace': 'no-wrap',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'maxWidth': '500px',
                    'textAlign':'left',
                    'font-size': '150%',
                },
                style_cell_conditional=[{
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }],
                style_header={
                    'backgroundColor': 'white',
                    'fontWeight': 'bold'
                },
                style_table={
                    'max_rows_in_viewport':15,
                    'maxHeight': '400px',
                    'maxWidth':'800px',
                    'overflowY': 'scroll',
                    'margin-left': '20px',
                    # 'border': 'thin lightgrey solid',
                }
            ),
                # html.H3('Select a dependency to see its tableau of PFDs'),
                html.Div(id='syn-container', className="six columns"),
                # html.Div(id='pfds-container-hidden', style={'display':'none'}),
            ], className="row ")
        else:
            return(html.Div(['']))

    elif tab == 'outliers':
        dmvs = gresults['DMVs']
        dmvs_list = []
        for ii in range(len(dmvs_list)):
            dmvs_list.remove(dmvs_list[0])
        for i in range(len(dmvs)):
            if 'OD' in dmvs[i]['DMV'][3]:
                dmvs_list.append(dmvs[i]['DMV'][0:3])
        # print (dmvs_list)
        if len(dmvs_list) > 0:
            dmvs_df = pd.DataFrame(dmvs_list, columns = ['Attribute', 'Value', 'Frequency'])
            return html.Div([
                dash_table.DataTable(
                data=dmvs_df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in dmvs_df.columns],
                id='od-table',
                row_selectable="single",
                # row_deletable=True,
                css=[{
                    'selector': '.dash-cell div.dash-cell-value',
                    'rule': 'display: inline; white-space: inherit; margin-left: 20px; overflow: inherit; text-overflow: inherit;'
                }],
                style_cell={
                    'whiteSpace': 'no-wrap',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'maxWidth': '500px',
                    'textAlign':'left',
                    'font-size': '150%',
                },
                style_cell_conditional=[{
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }],
                style_header={
                    'backgroundColor': 'white',
                    'fontWeight': 'bold'
                },
                style_table={
                    'max_rows_in_viewport':15,
                    'maxHeight': '400px',
                    'maxWidth':'800px',
                    'overflowY': 'scroll',
                    'margin-left': '20px',
                    # 'border': 'thin lightgrey solid',
                }
            ),
                # html.H3('Select a dependency to see its tableau of PFDs'),
                html.Div(id='od-container', className="six columns"),
                # html.Div(id='pfds-container-hidden', style={'display':'none'}),
            ], className="row ")
        else:
            return(html.Div(['']))

    elif tab == 'rand':
        dmvs = gresults['DMVs']
        dmvs_list = []
        for ii in range(len(dmvs_list)):
            dmvs_list.remove(dmvs_list[0])
        for i in range(len(dmvs)):
            if 'Rand' in dmvs[i]['DMV'][3]:
                dmvs_list.append(dmvs[i]['DMV'][0:3])
        # print (dmvs_list)
        if len(dmvs_list) > 0:
            dmvs_df = pd.DataFrame(dmvs_list, columns = ['Attribute', 'Value', 'Frequency'])
            return html.Div([
                dash_table.DataTable(
                data=dmvs_df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in dmvs_df.columns],
                id='rand-table',
                row_selectable="single",
                # row_deletable=True,
                css=[{
                    'selector': '.dash-cell div.dash-cell-value',
                    'rule': 'display: inline; white-space: inherit; margin-left: 20px; overflow: inherit; text-overflow: inherit;'
                }],
                style_cell={
                    'whiteSpace': 'no-wrap',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'maxWidth': '500px',
                    'textAlign':'left',
                    'font-size': '150%',
                },
                style_cell_conditional=[{
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }],
                style_header={
                    'backgroundColor': 'white',
                    'fontWeight': 'bold'
                },
                style_table={
                    'max_rows_in_viewport':15,
                    'maxHeight': '400px',
                    'maxWidth':'800px',
                    'overflowY': 'scroll',
                    'margin-left': '20px',
                    # 'border': 'thin lightgrey solid',
                }
            ),
                # html.H3('Select a dependency to see its tableau of PFDs'),
                html.Div(id='rand-container', className="six columns"),
                # html.Div(id='pfds-container-hidden', style={'display':'none'}),
            ], className="row ")
        else:
            return(html.Div(['']))



@app.callback(Output('dmvs-container-hidden', 'children'),
              [Input('fahes-table', 'data_previous')],
              [State('fahes-table', 'data')])
def show_removed_rows(previous, current):
    global gresults
    if previous is None:
        dash.exceptions.PreventUpdate()
    else:
        for row in previous:
            if row not in current:
                rem_att = row['Attribute']
                rem_val = row['Value']
                for jj in range(len(gresults['DMVs'])):
                    if gresults['DMVs'][jj]['DMV'][0] == row['Attribute'] and gresults['DMVs'][jj]['DMV'][1] == row['Value']:
                        gresults['DMVs'].remove(gresults['DMVs'][jj])
                        # print(gresults['pfds'][jj]['det'], gresults['pfds'][jj]['dep'], jj)
                        break
                # print(row['Determinant'][0], '===>', row['Dependent'][0])
        return html.Div([
                # html.H3('The selected attribute is ( ' + derived_virtual_selected_rows[0] + ' )')
                html.H3(""),
            ])





@app.callback(
    Output('syn-container', "children"),
    [Input('syn-table', "derived_virtual_data"),
     Input('syn-table', "derived_virtual_selected_rows")])
def update_graphs_patterns(rows, derived_virtual_selected_rows):
    # When the table is first rendered, `derived_virtual_data` and
    # `derived_virtual_selected_rows` will be `None`. This is due to an
    # idiosyncracy in Dash (unsupplied properties are always None and Dash
    # calls the dependent callbacks when the component is first rendered).
    # So, if `rows` is `None`, then the component was just rendered
    # and its value will be the same as the component's dataframe.
    # Instead of setting `None` in here, you could also set
    # `derived_virtual_data=df.to_rows('dict')` when you initialize
    # the component.
    global gresults, gdf
    # print(derived_virtual_selected_rows)
    if not(derived_virtual_selected_rows):
        derived_virtual_selected_rows = []
        return html.Div([
            html.H4('') 
        ], className="six columns")
    else:
        ptrns = gresults['PTRNs']
        for i in range(len(ptrns)):
            if rows[derived_virtual_selected_rows[0]]['Attribute'] == ptrns[i]['PTRN'][0]:
                idx_list = range(1, int((len(ptrns[i]['PTRN']) - 1)), 2)
                att_ptrns = []
                for kk in range(len(att_ptrns)):
                    att_ptrns.remove(att_ptrns[0])
                for ptrn_idx in idx_list:
                    att_ptrns.append((ptrns[i]['PTRN'][ptrn_idx], ptrns[i]['PTRN'][ptrn_idx+1]))
                # print (att_ptrns)
        
                patt_df = pd.DataFrame(att_ptrns, columns=['pattern (p)', '# distinct values represented by p'])
                return html.Div([
                    dash_table.DataTable(
                    data=patt_df.to_dict('records'),
                    columns=[{'name': i, 'id': i} for i in patt_df.columns],
                    id='ptrns-syn-table',
                    css=[{
                        'selector': '.dash-cell div.dash-cell-value',
                        'rule': 'display: inline; white-space: inherit; margin-left: 20px; overflow: inherit; text-overflow: inherit;'
                    }],
                    style_cell={
                        'whiteSpace': 'no-wrap',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                        'maxWidth': '600px',
                        'textAlign':'left',
                        'font-size': '150%',
                        'font-family': 'Times New Roman'
                    },
                    style_cell_conditional=[{
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }],
                    style_header={
                        'backgroundColor': 'white',
                        'fontWeight': 'bold'
                    },
                    style_table={
                        'max_rows_in_viewport':15,
                        'maxHeight': '400px',
                        'maxWidth':'800px',
                        'overflowY': 'scroll',
                        'margin-left': '20px',
                        # 'border': 'thin lightgrey solid',
                    }
                ),
                    # html.H3(gdf.columns[derived_virtual_selected_rows] + '   Just for test')
                ])
            # else:
            #     text = '(' + gdf.columns[derived_virtual_selected_rows[0]] + ') has been ignored because it represents ' 
            #     text += 'a numerical quantity '
            #     return html.Div([
            #         # html.H3('The selected attribute is ( ' + derived_virtual_selected_rows[0] + ' )')
            #         html.H3(text)
            #     ], className="six columns")
    return html.Div([
        # html.H3('The selected attribute is ( ' + derived_virtual_selected_rows[0] + ' )')
        html.H3('')
    ], className="six columns")




@app.callback(
    Output('od-container', "children"),
    [Input('od-table', "derived_virtual_data"),
     Input('od-table', "derived_virtual_selected_rows")])
def update_graphs_pfds(rows, derived_virtual_selected_rows):
    global gresults, gdf
    # print(derived_virtual_selected_rows)
    if not(derived_virtual_selected_rows):
        derived_virtual_selected_rows = []
        return html.Div([
            html.H4('') 
        ], className="six columns")
    else:
        req_att_name = rows[derived_virtual_selected_rows[0]]['Attribute']
        cur_dmv = rows[derived_virtual_selected_rows[0]]['Value']
        req_att_values = gdf[req_att_name]
        dmv_values_idx = gdf.index[gdf[req_att_name] == cur_dmv].tolist()
        normal_values_idx = list(set(gdf[req_att_name].index) - set(dmv_values_idx))
        # print(normal_values_idx)
        normal_values = gdf[req_att_name][normal_values_idx]
        # print(list(req_att_values))
        return html.Div([
            dcc.Graph(
                id='od-scatter',
                figure={
                    'data': [
                        go.Scatter(
                            x=normal_values_idx,
                            y=normal_values,
                            # text=df[df['continent'] == i]['country'],
                            mode='markers',
                            opacity=0.7,
                            marker={
                                'size': 10,
                                'line': {'width': 0.2, 'color': 'blue'}
                            },
                            name='Normal'
                        ),
                        go.Scatter(
                            x=gdf.index[gdf[req_att_name] == cur_dmv].tolist(),
                            y=[cur_dmv]*len(gdf.index[gdf[req_att_name] == cur_dmv].tolist()),
                            
                            # text=df[df['continent'] == i]['country'],
                            mode='markers',
                            opacity=0.7,
                            marker={
                                'size': 10,
                                'line': {'width': 0.2, 'color': 'red'}
                            },
                            name='DMV'
                        ),
                    ],
                    'layout': go.Layout(
                        xaxis={'title': 'Tuple count'},
                        yaxis={'title': req_att_name},
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest'
                    )
                }
            )
        ])

            
    return html.Div([
        # html.H3('The selected attribute is ( ' + derived_virtual_selected_rows[0] + ' )')
        html.H3('')
    ], className="six columns")







@app.callback(
    Output('rand-container', "children"),
    [Input('rand-table', "derived_virtual_data"),
     Input('rand-table', "derived_virtual_selected_rows")])
def update_graphs_vios(rows, derived_virtual_selected_rows):
    global gresults, gdf
    # print(derived_virtual_selected_rows)
    if not(derived_virtual_selected_rows):
        derived_virtual_selected_rows = []
        return html.Div([
            html.H4('') 
        ], className="six columns")
    else:
        req_att_name = rows[derived_virtual_selected_rows[0]]['Attribute']
        cur_dmv = rows[derived_virtual_selected_rows[0]]['Value']
        dmv_values_idx = gdf.index[gdf[req_att_name] == cur_dmv].tolist()
        rand_df = gdf.loc[dmv_values_idx]
        return html.Div([
            dash_table.DataTable(
            data=rand_df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in rand_df.columns],
            id='ptrns-syn-table',
            css=[{
                'selector': '.dash-cell div.dash-cell-value',
                'rule': 'display: inline; white-space: inherit; margin-left: 20px; overflow: inherit; text-overflow: inherit;'
            }],
            style_cell={
                'whiteSpace': 'no-wrap',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'maxWidth': '600px',
                'textAlign':'left',
                'font-size': '150%',
                'font-family': 'Times New Roman'
            },
            style_cell_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            },
            {'if': {'column_id': req_att_name},
                    'backgroundColor': 'lightblue',
                    },
            ],
            style_header={
                'backgroundColor': 'white',
                'fontWeight': 'bold'
            },
            style_table={
                'max_rows_in_viewport':15,
                'maxHeight': '400px',
                'maxWidth':'800px',
                'overflowY': 'scroll',
                'margin-left': '20px',
                # 'border': 'thin lightgrey solid',
            }
        ),
            # html.H3(gdf.columns[derived_virtual_selected_rows] + '   Just for test')
        ])
            # else:
            #     text = '(' + gdf.columns[derived_virtual_selected_rows[0]] + ') has been ignored because it represents ' 
            #     text += 'a numerical quantity '
            #     return html.Div([
            #         # html.H3('The selected attribute is ( ' + derived_virtual_selected_rows[0] + ' )')
            #         html.H3(text)
            #     ], className="six columns")
    return html.Div([
        # html.H3('The selected attribute is ( ' + derived_virtual_selected_rows[0] + ' )')
        html.H3('')
    ], className="six columns")





# # # # # # # # #
# detail the way that external_css and external_js work and link to alternative method locally hosted
# # # # # # # # #
external_css = ["https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",
                "https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "//fonts.googleapis.com/css?family=Raleway:400,300,600",
                "https://codepen.io/bcd/pen/KQrXdb.css",
                "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
                "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css",
                "https://www.w3schools.com/w3css/4/w3.css",
                "/assets/style.css"]

for css in external_css:
    app.css.append_css({"external_url": css})

external_js = ["https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js",
               "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js",
               ]

for js in external_js:
    app.scripts.append_script({"external_url": js})






if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port='8056')


