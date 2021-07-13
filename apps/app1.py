import plotly.express as px
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from app import app

from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from datetime import date
from Bb_Data.connect_bb_data import Blackboard_Data
from snowflake.connector import ProgrammingError


def load_data():
    df = pd.read_csv("/Users/edwardt/PycharmProjects/Bb_Dash/Bb_Data/LMS_Session.csv")

    df['Time'] = df['DATE'] + df['TWO_HOURS_INTERVAL_TWELVE_HOURS_FORMAT'].str.strip()
    df['Time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d%I %p')

    return df


df = load_data()

hours = df['TWO_HOURS_INTERVAL_TWELVE_HOURS_FORMAT'].str.strip().unique()

layout = html.Div([
    html.H3("This is Dashboard for active users"),

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
                            dbc.Button("Submit", color="primary", className="mr-1", id='submit',
                                       style={"margin-left": "15px"}),
                        ]
                    ),
                    width=6,
                ),
            ],
            form=True,
        ),
        html.Div(id='body-div1'),
        dcc.Checklist(
            id="checklist",
            options=[{"label": x, "value": x}
                     for x in hours],
            value=hours,
            labelStyle={'display': 'inline-block'}
        ),
        dcc.Graph(id="line-chart"),
    ]),
    html.Div(id='hidden-df', style={'display': 'none'})

]),


@app.callback(
    Output('hidden-df', 'value'),
    Input('submit', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),

)
def update_output(n_clicks, start_date=None, end_date=None):
    if n_clicks is None:
        raise PreventUpdate
    else:
        try:
            bb = Blackboard_Data()
            bb.get_active_users(start_date, end_date)
            df = load_data()
            return df.to_json(date_format='iso', orient='split')
        except ProgrammingError as err:
            print('Programming Error: {0}'.format(err))

            # return dbc.Alert(f"New Report has Generated between {start_date} and {end_date}. Good to know!",
            #              color="success")


@app.callback(
    Output('body-div1', 'children'),
    Input('submit', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),

)
def updated_message(n_clicks, start=None, end=None):
    if n_clicks is None:
        raise PreventUpdate
    else:
        return dbc.Alert(f"New Report has Generated between {start} and {end}. Good to know!",
                         color="success")


@app.callback(
    Output("line-chart", "figure"),
    Input("checklist", "value"),
    Input('hidden-df', 'value')
)
def update_line_chart(updates, value):
    df = load_data()
    if value:
        # global df
        df = pd.read_json(value, orient='split')

    fil = df['TWO_HOURS_INTERVAL_TWELVE_HOURS_FORMAT'].str.strip().isin(updates)
    fig = px.line(df[fil],
                  x="Time", y="LMS_SESSION_COUNT", hover_data={"Time": "|%B %d, %Y %I%p(%A)"},
                  title='Active users in Blackboard')
    return fig
