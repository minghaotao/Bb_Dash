import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from app import app

from dash.exceptions import PreventUpdate
from datetime import date
from Bb_Data.connect_bb_data import Blackboard_Data
from snowflake.connector import ProgrammingError


def load_data():
    df_tools = pd.read_csv("/Users/edwardt/PycharmProjects/Bb_Dash/Bb_Data/Tool_Usage.csv")

    df_tools['MONTH'] = pd.to_datetime(df_tools['MONTH']).dt.strftime('%m').astype(int)

    df_tools.set_index('TOOL_ID', inplace=True)

    df_tools = df_tools.drop(
        df_tools.index.intersection([88, 174, 50, 49, 24, 294, 49, 91, 74, 249, 221, 22, 281, 123, 155, 221]))
    return df_tools


df_tools = load_data()

layout = html.Div(children=[
    html.H3("Blackboard Tool Usage"),

    html.Div(children=[
        dbc.Row(
            [
                dbc.Col(
                    dbc.FormGroup(
                        [
                            dbc.Label("Select Date", html_for="example-email-grid"),
                            html.Br(),
                            dcc.DatePickerRange(
                                id='my-date-picker-range',
                                min_date_allowed=date(2018, 8, 5),
                                max_date_allowed=date(2023, 9, 19),
                                initial_visible_month=date(2021, 1, 1),
                                end_date=date(2021, 8, 25),
                            ),
                        ]
                    ),
                    width=6,
                ),
                dbc.Col(
                    dbc.FormGroup(
                        [
                            dbc.Label("Semester", html_for="example-password-grid"),
                            dbc.Input(id="input", placeholder="Semester", type="text"),
                        ]
                    ),
                    width=6,
                ),
            ],
            form=True,
        ),
        dbc.Button("Re-generate Report", color="primary", block=True, id='show-secret'),
        html.Div(id='body-div')

    ]),

    html.Br(),
    dcc.Dropdown(
        id='tools_dropdown',
        options=[
            {'label': 'All', 'value': 'All'},
            {'label': 'Blackboard Assessment', 'value': 'Assessment'},
            {'label': 'Tech Tools', 'value': 'Tech'}

        ],
        value='All'

    ),

    dcc.Graph(id='graph-with-slider'),
    dcc.Slider(
        id='month-slider',
        min=df_tools['MONTH'].min(),
        max=df_tools['MONTH'].max(),
        value=df_tools['MONTH'].min(),
        marks={str(MONTH): str(MONTH) for MONTH in df_tools['MONTH'].unique()},
        step=None
    ),
    html.Br(),
    html.Div(id='hidden-df1', style={'display': 'none'})

]),


@app.callback(
    # Output(component_id='body-div', component_property='children'),
    Output('hidden-df1', 'data'),
    Input(component_id='show-secret', component_property='n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),
    Input("input", "value"),

)
def update_output(n_clicks, start_date=None, end_date=None, input=None):
    if n_clicks is None:
        raise PreventUpdate
    else:
        try:
            bb = Blackboard_Data()
            bb.get_tools_usage(start_date, end_date, input)

            df_tools = load_data()

            return df_tools.to_json(date_format='iso', orient='split')

        except ProgrammingError as err:
            print('Programming Error: {0}'.format(err))

        # return dbc.Alert(f"New Report has Generated between {start_date} and {end_date}. Good to know!",
        #                  color="success")


@app.callback(
    Output('graph-with-slider', 'figure'),
    Input('month-slider', 'value'),
    Input('tools_dropdown', 'value'),
    Input('hidden-df1', 'data')

)
def update_figure(selected_year, selected_tool, data=None):
    if data:
        global df_tools
        df_tools = pd.read_json(data, orient='split')

    filtered_df = df_tools[df_tools.MONTH == selected_year]

    if selected_tool == 'All':
        filtered_df = filtered_df.drop(filtered_df.index.intersection([138, 118, 126, 69]))
        fig = px.scatter(filtered_df, x="COURSES", y="USERS",
                         size="TIMES_OF_ACCES", color=filtered_df["TOOL_NAME"], hover_name="TOOL_NAME",
                         log_x=True, size_max=55, title='Blackboard Tool Usage')
        fig.update_layout(transition_duration=500)

        return fig

    if selected_tool == 'Assessment':
        selected_tool = [138, 118, 126, 69]
    if selected_tool == 'Tech':
        selected_tool = [281, 125, 247, 165, 38864, 119, 130, 258, 79100, 99, 179, 157, 141, 167, 215, 121, 143, 276]

    fig = px.scatter(filtered_df.loc[filtered_df.index.intersection(selected_tool)], x="COURSES", y="USERS",
                     size="TIMES_OF_ACCES", color="TOOL_NAME", hover_name="TOOL_NAME",
                     log_x=True, size_max=55, title='Blackboard Tool Usage')

    fig.update_layout(transition_duration=500)

    return fig
