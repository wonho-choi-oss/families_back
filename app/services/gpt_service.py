from flask import Blueprint, request, abort, current_app, jsonify
from openai import OpenAI
from app import db
from app.models import GptUser, GptBot
from datetime import datetime

def get_gpt_reply(user_message):
    now = datetime.now()

    date_part = now.strftime("%Y-%m-%d")
    time_part = now.strftime("%I:%M").lstrip('0')  # "05:47" -> "5:47"
    ampm_part = now.strftime("%p")

    print('date_part',date_part)

    client = OpenAI(api_key=current_app.config['OPENAI_API_KEY'])

    timestamp = now.strftime("%Y-%m-%d") + " " + user_message[0].get('timestamp')
    content = user_message[0].get('content')
    role = user_message[0].get('role')
    date = date_part

    user_new_data = GptUser(content=content, role=role, timestamp=timestamp, date=date)

    db.session.add(user_new_data)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=user_message
    )

    gpt_reply = response.choices[0].message.content

    content = gpt_reply
    role = 'bot'
    timestamp = f"{date_part} {time_part} {ampm_part}"

    bot_new_data = GptBot(content=content, role=role, timestamp=timestamp, date=date, owner=user_new_data)

    db.session.add(bot_new_data)

    db.session.commit()

    results = db.session.query(GptUser, GptBot) \
        .join(GptBot, GptUser.id == GptBot.worksheet_id) \
        .filter(GptUser.id == 3) \
        .all()

    formatted_results = [
        {
            "id": u.id,
            "user_msg": u.content,
            "bot_msg": b.content,
            "date": u.date
        } for u, b in results
    ]

    print('~~~~~~~~~',formatted_results)
    return gpt_reply



