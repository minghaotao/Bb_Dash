import dash
import plotly.express as px
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.read_csv("/Users/edwardt/PycharmProjects/Bb_Dash/Bb_Data/LMS_Session.csv")

df['Time'] = df['DATE'] + df['TWO_HOURS_INTERVAL_TWELVE_HOURS_FORMAT'].str.strip()
df['Time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d%I %p')

hours = df['TWO_HOURS_INTERVAL_TWELVE_HOURS_FORMAT'].str.strip().unique()

app.layout = html.Div([
    html.H3("This is Dashboard for active users"),
    dcc.Checklist(
        id="checklist",
        options=[{"label": x, "value": x}
                 for x in hours],
        value=hours,
        labelStyle={'display': 'inline-block'}
    ),
    dcc.Graph(id="line-chart"),
])


@app.callback(
    Output("line-chart", "figure"),
    [Input("checklist", "value")])
def update_line_chart(continents):
    fil = df['TWO_HOURS_INTERVAL_TWELVE_HOURS_FORMAT'].str.strip().isin(continents)
    fig = px.line(df[fil],
                  x="Time", y="LMS_SESSION_COUNT", hover_data={"Time": "|%B %d, %Y %I%p(%A)"},
                  title='Active users in Blackboard')
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
