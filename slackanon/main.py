#!/usr/bin/env python3

from flask import Flask, request
from os import getenv
import requests
import logging

app = Flask(__name__)


@app.route("/")
def home_view():
    return "<h1>Works!</h1>"


def slack_post_message(channel, text):
    slack_token = getenv("SLACK_TOKEN")
    if not slack_token:
        raise KeyError("Set SLACK_TOKEN")
    app.logger.log(level=logging.INFO,
                   msg="Sending '{}' to '{}'".format(text, channel))
    result = requests.post(url="https://slack.com/api/chat.postMessage",
                           headers={
                               "Authorization": "Bearer {}".format(slack_token)
                           },
                           json={
                               "channel": channel,
                               "text": "Кое-кто отправил послание: " + text
                           })
    app.logger.log(level=logging.INFO,
                   msg="Got {code} from slack when sending message,\nbody {body}\n".format_map({
                       "code": result.status_code,
                       "body": result.content
                   }))
    return result


def get_message_destination(message_text):
    first_word = message_text.split(" ")[0]
    if first_word.startswith("<") and first_word.endswith(">"):
        return first_word[1:-1].split("|")[0][1:]
    else:
        return None


def get_message_content(message_text):
    words = message_text.split(" ")
    if words[0].startswith("<") and words[0].endswith(">"):
        return " ".join(words[1:])
    else:
        return message_text


# noinspection PyBroadException
@app.route("/slash", methods=["POST"])
def slash():
    app.logger.log(level=logging.INFO,
                msg="Received request from {user},\nfields:\n{fields},\ndata: {data}\n".format_map({
                    "data": request.get_data().decode("UTF-8"),
                    "user": request.form["user_name"],
                    "fields": "\n".join(["\t" + key + ": " + value for key, value in request.form.items()])
                }))
    try:
        destination = get_message_destination(request.form["text"])
        slack_post_message(destination if destination else request.form["channel_id"],
                           get_message_content(request.form["text"]))
        return "Сообщение отправлено :orange_heart:", 200  # if destination else ("", 200)
    except BaseException:
        app.logger.log(level=logging.ERROR,
                       msg="Received request from {user}, got error" +
                           ",\nfields:\n{fields},\ndata: {data}\n".format_map({
                            "data": request.get_data().decode("UTF-8"),
                            "user": request.form["user_name"],
                            "fields": "\n".join(["\t" + key + ": " + value for key, value in request.form.items()])
                            }))
        return "Сообщение не отправлено", 200

