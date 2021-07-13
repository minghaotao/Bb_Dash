import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from app import app
from apps import app1, app2

# app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H4("Bb Dash", className="display-4"),
        html.Hr(),
        html.P(
            "FHSU Blackboard Interactive DashBoard - Edward Tao", className="lead"
        ),
        dbc.Nav(
            [
                # dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Active Users", href="/Users/edwardt/PycharmProjects/Bb_Dash/apps/app1", active="exact"),
                dbc.NavLink("Tool Usage", href="/Users/edwardt/PycharmProjects/Bb_Dash/apps/app2", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/Users/edwardt/PycharmProjects/Bb_Dash/apps/app1":
        return app1.layout
    elif pathname == "/Users/edwardt/PycharmProjects/Bb_Dash/apps/app2":
        return app2.layout
    elif pathname == "/":
        return app1.layout

    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


if __name__ == "__main__":
    app.run_server(debug=True)
