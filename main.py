import os
import time
import requests
import json
from bs4 import BeautifulSoup
from flask import Flask, jsonify
import threading

app = Flask(__name__)


def get_courses():
    while True:
        dev_url = 'http://127.0.0.1:10000'
        production_url = 'https://free-udemy-course.onrender.com'

        response = requests.get(f"{production_url}/getcourses")
        if response.status_code == 200:
            print("Courses updated successfully")

        time.sleep(1800)


@app.route('/getcourses/', methods=['GET', 'POST'])
def check_course_links():
    r= ''
    url = "https://www.discudemy.com/all"
    response = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    })
    soup = BeautifulSoup(response.text, "html.parser")

    mainCourses = soup.select('.ui.four.stackable.cards.m15 .card')

    course_links = []
    for course in mainCourses:
        header = course.select_one('.content > .header')
        descriptions = course.select_one('.content > .description')
        if header:
            a_tag = header.select_one('a')
            if a_tag:
                title = a_tag.text
                description = descriptions.text.strip()
                a_tag_href = a_tag.get('href')
                if a_tag_href:
                    modified_a_tag = a_tag_href.split('/')
                    modified_a_tag[3] = 'go'
                    modified_a_tag_url = '/'.join(modified_a_tag)
                    modified_response = requests.get(modified_a_tag_url, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    })
                    modified_soup = BeautifulSoup(
                        modified_response.text, "html.parser")
                    course_link = modified_soup.select_one(
                        '.ui.segment > a')['href']

                    final_msg = {
                        'title': title,
                        'description': description,
                        'link': course_link
                    }

                    course_links.append(final_msg)

    # Check if new courses have been added
    if os.path.exists('course_links.json'):
        with open('course_links.json', 'r') as f:
            old_course_links = json.load(f)

        for new_course in course_links:
            if new_course not in old_course_links:
                msg = {
                    'chat_id': -1001963897851,
                    'text': f'<b>Title: </b>{new_course["title"]}\n\n<b>Description: </b>{new_course["description"]}\n\n<b>Link: </b>{new_course["link"]}',
                    'parse_mode': 'HTML'
                }
                time.sleep(2)
                r = requests.post(
                    url=f'https://api.telegram.org/bot6368396099:AAFSnR1OT3RPg3cBd6r7pqNZSqQoKVjMnHQ/sendMessage', params=msg)
                if r.status_code == 200:
                    print("New course added:", new_course['title'])

                # Save the course links to a JSON file
                with open('course_links.json', 'w') as f:
                    json.dump(course_links, f, indent=4)

    return jsonify(r.text)


@app.route('/')
def index():
    return "Task scheduled to update courses every 30 Minutes."


if __name__ == '__main__':
    thread = threading.Thread(target=get_courses)
    thread.daemon = True
    thread.start()

    app.run(host='0.0.0.0', port=10000, debug=False)
