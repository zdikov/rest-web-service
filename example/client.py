import requests
import time

URL = 'http://172.21.0.5:5000'
USERS_ENDPOINT = '/api/v1.0/users'
STATS_ENDPOINT = '/api/v1.0/stats'

input_data = {"name": "user1",
              "gender": "male",
              "email": "user@example.com",
              "avatar_url": "https://jrnlst.ru/sites/default/files/covers/cover_6.jpg"
              }

response = requests.post(URL + USERS_ENDPOINT, json=input_data)
response = requests.get(URL + f'{USERS_ENDPOINT}/stats/{response.json()["user_id"]}')

time.sleep(1)

response = requests.get(URL + response.json()["url"])
assert response.ok

open('report.pdf', 'wb').write(response.content)
