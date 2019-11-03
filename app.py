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
import plotly_express as px
# languge
from collections import defaultdict
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import pprint
from gensim import corpora
from gensim import models
from gensim import similarities


###########################################
# GETTING DATA
###########################################
df_discussions = pd.read_csv(
    "data/2019-11-02_reddit-data-learnmath_scrubbed.csv")


##############################################
# BUILDING MODEL
##############################################


def convert_csv_to_list(posts_df):

    # take only the combined column
    posts_df = posts_df["combined"]

    # Convert the column to a list
    corpus_text = list()
    for row in range(posts_df.shape[0]):
        temp = posts_df.iloc[row]
        corpus_text.append(temp)

    # Convert the list to list of lists
    processed_corpus = list()

    stem_sentence = []
    porter = PorterStemmer()

    for text in corpus_text:

        token_words = word_tokenize(text)
        token_words
        stem_sentence = []
        for word in token_words:
            stem_sentence.append(porter.stem(word))
            stem_sentence.append(" ")
#         # tokenize it
#         tokenized_list = word_tokenize(text)

        # convert to lower case
        tokenized_list = [w.lower() for w in stem_sentence]

        # get the alphabetic words
        words = [word for word in tokenized_list if word.isalpha()]

        # get rid of stop words
        words = [w for w in words if not w in stop_words]

        processed_corpus.append(words)

    return processed_corpus  # list of lists


def train_model(corpus):
    dictionary_reddit = corpora.Dictionary(corpus)
    num_words = len(dictionary_reddit.keys())

    # convert to a bag of words reprensentation
    bow_corpus_reddit = [dictionary_reddit.doc2bow(text) for text in corpus]

    # train the model
    tfidf_reddit = models.TfidfModel(bow_corpus_reddit)

    # similarities model
    index_reddit = similarities.SparseMatrixSimilarity(tfidf_reddit[bow_corpus_reddit],
                                                       num_features=num_words)
    return index_reddit, dictionary_reddit, tfidf_reddit


# build model
stop_words = stopwords.words('english')
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
                      type="text", size="75"),
            html.Br(),
            html.Br(),
            html.Label("New message:"),
            dcc.Input(id="topic_message", placeholder="Message Details",
                      type="text", size="75", style={'height': 250}),
            html.Hr(),
            html.H5("Existing discussions"),
            html.Label("Check if your question has already been answered:"),
            html.Div(id="topic_prediction"),
            html.Table(generate_table(df_discussions, 5))
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
    topic_string = topic_string.lower()
    return 'You\'ve entered "{}"'.format(topic_string)


# if __name__ == '__main__':
#     app.run_server(debug=True)