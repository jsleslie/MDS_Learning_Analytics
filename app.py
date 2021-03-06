# base
import datetime
import socket
import os
import re
# external libraries
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import nltk
import json
import pandas as pd
import plotly.graph_objs as go
# language
from collections import defaultdict
# helpers
from helpers import *


###########################################
# GET DATA
###########################################
df1 = pd.read_csv(
    "data/2019-11-02_reddit-data-learnmath_scrubbed.csv")
df2 = pd.read_csv(
    "data/2019-11-02_reddit-data-askscience_scrubbed.csv")
df_discussions = pd.concat([df1, df2]).reset_index()


##############################################
# BUILDING MODEL
##############################################
discussion_lists = convert_csv_to_list(df_discussions)
model = train_model(discussion_lists)


###########################################
# STATIC FUNCTIONS
###########################################
def generate_table(df, max_rows=10):
    """
    Renders a table in dash app

    Arguments:
        df {pd.DataFrame} -- Data frame to render

    Keyword Arguments:
        max_rows {int} -- number of rows to render (default: {10})

    Returns:
        html.Table -- table ready to be rendered by
    """
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in df.columns])] +
        # Body
        [html.Tr([
            html.Td(df.iloc[i][col]) for col in df.columns
        ]) for i in range(min(len(df), max_rows))]
    )


###########################################
# APP LAYOUT
###########################################

# COLOUR AND STYLE
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

colors = {"white": "#ffffff",
          "light_grey": "#d2d7df",
          "ubc_blue": "#082145"
          }


# APP LAYOUT
app.layout = html.Div(style={'backgroundColor': colors['light_grey']}, children=[
    # HEADER
    html.Div(className="row", style={'backgroundColor': colors['ubc_blue'], "padding": 10}, children=[
        html.H2('UBC Canvas Discussion Board Demo',
                style={'color': colors['white']})
    ]),
    # MAIN BODY
    html.Div(className="row", children=[
        # SIDEBAR
        html.Div(className="two columns", style={'padding': 20}, children=[
            html.Img(src="assets/ubc-logo-2.png", width="50"),
            html.P("Home\nAnnouncements\nDiscussions\nGrades\nPeople")
        ]),
        # DISCUSSION BOARD
        html.Div(className="ten columns", style={"backgroundColor": colors['white'], "padding": 20}, children=[
            html.H4("Start a new discussion"),
            html.Label("New topic title:"),
            dcc.Input(id="topic_title", placeholder="Topic Title",
                      type="text", size="75", value=""),
            html.Br(),
            html.Br(),
            html.Label("New message:"),
            dcc.Input(id="topic_message", placeholder="Message Details",
                      type="text", size="75", style={'height': 250}),
            html.Br(),
            html.Br(),
            html.Button('Submit', id='button'),
            html.Hr(),
            html.H5("Existing discussions"),
            html.Div(id="topic_prediction")
        ])
    ])
])

###########################################
# APP CALL BACKS
###########################################

@app.callback(
    Output(component_id='topic_prediction', component_property='children'),
    [Input(component_id='topic_title', component_property='value')]
)
def update_output_div(input_value):
    topic_string = str(input_value)
    dataframe_index = test_model(topic_string, model[0], model[1], model[2])
    if dataframe_index:
        out = df_discussions.loc[dataframe_index, [
            "discussion_topic_title", "thread_ref_link"]]
        out.rename(columns={"discussion_topic_title": "Topic Title",
                            "thread_ref_link": "URL"}, inplace=True)
        out["URL"] = out["URL"].apply(lambda x: html.A("link", href=x))
        out = generate_table(out)
        return out
    else:
        return 'No similar questions found, please post your question!'


if __name__ == '__main__':
    app.run_server(debug=False)
