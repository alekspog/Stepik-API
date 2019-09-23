# Run with Python 3
# Translate all steps texts from course.
import logging
import requests
from urllib.parse import quote
from googletrans import Translator


logger = logging.getLogger(__name__)

# Enter parameters below:
# 1. Get your keys at https://stepik.org/oauth2/applications/
# (client type = confidential, authorization grant type = client credentials)
client_id = "DKAOgdHrEaVBgshlsLllp9YTtRTXxUImQyVznrBY"
client_secret = "EZIAoy31Q4V0YF8lDmHqgWOluVn5trNVM54XBgC2doi0zcdsYKT2vCeQc1ZcjR5AMD1QVTXzX9nmxT81AvlkNoA0Yo7Vuv2OHtVepHlEKblfit38eOfKEBPwGm0dhiTn"
api_host = 'https://stepik.org'
course_id = 1

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
    if len(quote(text)) > TRANSLATIONS_GOOGLE_TRANSLATE_TEXT_MAX_LENGTH:
        print('Text too large (raw=%s, quoted=%s) to translate with google translator: %s',
                    len(text), len(quote(text)), text)
        return None

    translator = Translator()
    translation = translator.translate(text, dest='en')
    print(f'dest_text: {translation.text}')
    return translation.text


def translate_step(step_id):
    obj_class = 'step-source'
    obj_id = step_id
    api_url = '{}/api/{}s/{}'.format(api_host, obj_class, obj_id)
    response = requests.get(api_url,
                            headers={'Authorization': 'Bearer ' + token}).json()
    print(response)
    name = response[f'{obj_class}s'][0]['block']['name']
    text = response[f'{obj_class}s'][0]['block']['text']
    lesson_id = response[f'{obj_class}s'][0]['lesson']
    position = response[f'{obj_class}s'][0]['position']
    print(f'Try to translate text: {text}')
    text = translate(text)
    response[f'{obj_class}s'][0]['block']['text'] = text
    print(response[f'{obj_class}s'][0])
    if name == 'text':
        data = {
            'stepSource': {
                'block': {
                    'name': name,
                    'text': text,
                },
                'lesson': lesson_id,
                'position': position
            }
        }
    else:
        data = {
            'stepSource': response[f'{obj_class}s'][0]
        }
    response = requests.put(api_url,
                 headers={'Authorization': 'Bearer ' + token},
                 json=data
                 )
    print(response)

# course = fetch_object('course', course_id)
# sections = fetch_objects('section', course['sections'])
#
# unit_ids = [unit for section in sections for unit in section['units']]
# units = fetch_objects('unit', unit_ids)
#
# lesson_ids = [unit['lesson'] for unit in units]
# lessons = fetch_objects('lesson', lesson_ids)
#
# step_ids = [step for lesson in lessons for step in lesson['steps']]
# steps = fetch_objects('step', step_ids)
# https://stepik.org/lesson/50788/step/2
translate_step(203699)
