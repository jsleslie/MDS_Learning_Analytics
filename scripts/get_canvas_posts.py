import dotenv
import os
import pandas as pd
import requests
import json

def get_canvas_data(write_csv=False):
    """
    Queries canvas API to return discussion topics for selected course.
    For the script to work you must create a .evn file that contains:
        CANVAS_API_TOKEN=...
    In .. paste your token there

    Keyword Arguments:
        write_csv {bool} -- if True writes data to disk (default: {False})

    Returns:
        pd.DataFrame -- [description]
    """
    # API TOKEN
    dotenv.load_dotenv(dotenv.find_dotenv())
    TOKEN = os.environ.get('CANVAS_API_TOKEN')

    # API CALL
    # https://<canvas>/api/v1/courses/<course_id>/discussion_topics \
    url_base = 'https://ubc.instructure.com'
    url_1 = '/api/v1/courses/'
    course_id = 46341  # 46341 canvas hackathon
    url_2 = '/discussion_topics'
    url = url_base + url_1 + str(course_id) + url_2
    headers = {'Authorization': 'Bearer ' + TOKEN}

    # GET DATA
    r = requests.get(url, headers=headers)
    data = r.json()  # returns a list of dictionaries containg post information

    # PARSE AND CLEAN DATA
    post_id = list()
    discussion_topic_title = list()
    discussion_topic_message = list()
    url = list()

    for i in range(len(data)):
        post_id.append(data[i]["id"])
        discussion_topic_title.append(data[i]["title"])
        discussion_topic_message.append(data[i]["message"])
        url.append(data[i]["url"])

    df = pd.DataFrame({"post_id": post_id,
                       "discussion_topic_title": discussion_topic_title,
                       "discussion_topic_message": discussion_topic_message,
                       "url": url})

    if write_csv:
        df.to_csv("data/canvas-discussion-posts.csv", index=False)

    return df


df = get_canvas_data(write_csv=True)
print(df.info())
