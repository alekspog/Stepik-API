# Run with Python 3
# Translate all steps texts from course.
import html
import logging
import requests

from googletrans import Translator

import time


logger = logging.getLogger(__name__)

# Enter parameters below:
# 1. Get your keys at https://stepik.org/oauth2/applications/
# (client type = confidential, authorization grant type = client credentials)

api_host = 'https://stepik.org'
# course_id = 57922
course_id = 58150


DEST_LANG = "en"
SRC_LANG = "ru"
REQUESTS_PER_SECOND = 2
TRANSLATIONS_GOOGLE_TRANSLATE_TEXT_MAX_LENGTH = 15000


# 2. Get a token
auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
response = requests.post('https://stepik.org/oauth2/token/',
                         data={'grant_type': 'client_credentials'},
                         auth=auth)
token = response.json().get('access_token', None)
if not token:
    print('Unable to authorize with provided credentials')
    exit(1)


# 3. Call API (https://stepik.org/api/docs/) using this token.
def fetch_object(obj_class, obj_id):
    api_url = '{}/api/{}s/{}'.format(api_host, obj_class, obj_id)
    response = requests.get(api_url,
                            headers={'Authorization': 'Bearer ' + token}).json()
    z = response['{}s'.format(obj_class)][0]
    print(f'fetch response: {z}')
    return response['{}s'.format(obj_class)][0]


def fetch_objects(obj_class, obj_ids, keep_order=True):
    objs = []
    # Fetch objects by 30 items,
    # so we won't bump into HTTP request length limits
    step_size = 30
    for i in range(0, len(obj_ids), step_size):
        obj_ids_slice = obj_ids[i:i + step_size]
        api_url = '{}/api/{}s?{}'.format(api_host, obj_class,
                                         '&'.join('ids[]={}'.format(obj_id)
                                                  for obj_id in obj_ids_slice))
        response = requests.get(api_url,
                                headers={'Authorization': 'Bearer ' + token}
                                ).json()

        objs += response['{}s'.format(obj_class)]
    if (keep_order):
        return sorted(objs, key=lambda x: obj_ids.index(x['id']))
    return objs


def translate(text: str):

    translator = Translator()

    i = 0
    translated_text = ""
    while i < len(text):
        if text[i] == "<":
            print("collect tag")
            while True:
                translated_text += text[i]
                if text[i] == ">":
                    i += 1
                    break

                i += 1
            continue

        text_slice = ""
        print("collect text slice")
        while i < len(text):
            print("symbol: ", text[i])
            text_slice += text[i]
            print("text slice: ", text_slice)
            i += 1
            if i == len(text) or text[i] == "<":
                text_slice_escaped = html.unescape(text_slice)
                print("escaped ", text_slice_escaped)

                try:
                    lang = translator.detect(text_slice_escaped).lang
                    print("detected language: ", lang)
                    if lang == DEST_LANG:
                        print(f"Text is translated yet to {lang}")
                        translated_text_slice = text_slice_escaped
                        print("!!! translated text slice: ", translated_text_slice)
                        translated_text += translated_text_slice
                        print("!!!", translated_text)

                        break

                except Exception as e:
                    logger.warning('Google translator error: %s', e, exc_info=True)

                try:
                    translated_text_slice = translator.translate(
                        text_slice_escaped, dest=DEST_LANG, src=SRC_LANG).text
                    print("!!! translated text slice: ", translated_text_slice)
                    translated_text += translated_text_slice
                    print("!!!", translated_text)

                except Exception as e:
                    logger.warning('Google translator error: %s', e, exc_info=True)
                    break

                break


    # print(f'dest_text: {translation.text}')
    # return translation.text
    print(f'dest_text: {translated_text}')
    return translated_text


def translate_course(course):
    translate_course_info(course)

    sections = fetch_objects('section', course['sections'])

    unit_ids = [unit for section in sections for unit in section['units']]
    units = fetch_objects('unit', unit_ids)

    lesson_ids = [unit['lesson'] for unit in units]
    lessons = fetch_objects('lesson', lesson_ids)

    step_ids = [step for lesson in lessons for step in lesson['steps']]
    steps = fetch_objects('step', step_ids)

    for section in sections:
        translate_section(section)

    for lesson in lessons:
        translate_lesson(lesson)

    for step in steps:
        translate_step(step)


def translate_course_info(course):
    obj_class = 'course'
    obj_id = int(course['id'])
    api_url = '{}/api/{}s/{}'.format(api_host, obj_class, obj_id)
    object = fetch_object(obj_class, obj_id)

    if 'description' in object:
        description = object['description']
        print(f'Try to translate course description: {description}')
        description = translate(description)
        print(f'Translated course description: {description}')
        object['description'] = description
    else:
        description = None

    if 'requirements' in object:
        requirements = object['requirements']
        print(f'Try to translate course requirements: {requirements}')
        requirements = translate(requirements)
        print(f'Translated course requirements: {requirements}')
        object['requirements'] = requirements
    else:
        requirements = None

    if 'requirements_literature' in object:
        requirements_literature = object['requirements_literature']
        print(f'Try to translate course requirements literature: {requirements_literature}')
        requirements_literature = translate(requirements_literature)
        print(f'Translated course requirements literature: {requirements_literature}')
        object['requirements_literature'] = requirements_literature
    else:
        requirements_literature = None

    if 'summary' in object:
        summary = object['summary']
        print(f'Try to translate course summary: {summary}')
        summary = translate(summary)
        print(f'Translated course summary: {summary}')
        object['summary'] = summary
    else:
        summary = None

    if 'target_audience' in object:
        target_audience = object['target_audience']
        print(f'Try to translate course target_audience: {target_audience}')
        target_audience = translate(target_audience)
        print(f'Translated course target_audience: {target_audience}')
        object['target_audience'] = target_audience
    else:
        target_audience = None

    title = object['title']
    print(f'Try to translate course title: {title}')
    title = translate(title)
    print(f'Translated course title: {title}')
    object['title'] = title

    if 'workload' in object:
        workload = object['workload']
        print(f'Try to translate course workload: {workload}')
        workload = translate(workload)
        print(f'Translated course workload: {workload}')
        object['workload'] = workload
    else:
        workload = None

    data = {
        'course': {
            'description': description,
            'requirements': requirements,
            'requirements_literature': requirements_literature,
            'summary': summary,
            'target_audience': target_audience,
            'title': title,
            'workload': workload
        }
    }
    print(f'data: {data}')
    response = requests.put(api_url,
                 headers={'Authorization': 'Bearer ' + token},
                 json=data
                 )
    print(response)
    time.sleep(1/REQUESTS_PER_SECOND)


def translate_lesson(lesson):
    obj_class = 'lesson'
    obj_id = int(lesson['id'])
    api_url = '{}/api/{}s/{}'.format(api_host, obj_class, obj_id)
    object = fetch_object(obj_class, obj_id)
    print(object)
    text = object['title']
    print(f'Try to translate lesson title: {text}')
    text = translate(text)
    print(f'Translated lesson title: {text}')
    object['title'] = text
    data = {
        'lesson': {
            'title': text
        }
    }
    print(f'data: {data}')
    response = requests.put(api_url,
                 headers={'Authorization': 'Bearer ' + token},
                 json=data
                 )
    print(response)
    time.sleep(1/REQUESTS_PER_SECOND)


def translate_section(section):
    obj_class = 'section'
    obj_id = int(section['id'])
    api_url = '{}/api/{}s/{}'.format(api_host, obj_class, obj_id)
    object = fetch_object(obj_class, obj_id)
    print(object)
    text = object['title']
    print(f'Try to translate section title: {text}')
    text = translate(text)
    print(f'Translated section title: {text}')
    object['title'] = text
    data = {
        'section': {
            'title': text
        }
    }
    print(f'data: {data}')
    response = requests.put(api_url,
                 headers={'Authorization': 'Bearer ' + token},
                 json=data
                 )
    print(response)
    time.sleep(1/REQUESTS_PER_SECOND)


def translate_step(step):
    obj_class = 'step-source'
    obj_id = int(step['id'])
    api_url = '{}/api/{}s/{}'.format(api_host, obj_class, obj_id)
    object = fetch_object(obj_class, obj_id)
    name = object['block']['name']
    text = object['block']['text']
    lesson_id = object['lesson']
    position = object['position']
    print(f'Try to translate text: {text}')
    text = translate(text)
    print(f'Translated step text: {text}')
    object['block']['text'] = text
    print(object)
    data = {
        'stepSource': object
    }
    response = requests.put(api_url,
                 headers={'Authorization': 'Bearer ' + token},
                 json=data
                 )
    print(response)
    time.sleep(1/REQUESTS_PER_SECOND)


course = fetch_object('course', course_id)

# translate_course(course)

# translate("С:\\Users\\Юлия\\environments&gt; python\n")

# import json
# data = '"\\"foo\\bar"'
# converted = json.loads(data)
# translate("<p>work↵↵</p><p>работа↵↵</p>")
translate("<p>home</p><p>дом</p>")
