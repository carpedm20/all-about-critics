import json
import pandas as pd

movies = json.loads(open('compact.json').read())
data = json.loads(open('result.json').read())

new_data = []
for key, value in data.items():
    value['mid'] = key
    new_data.append(value)

movies = pd.DataFrame(movies)
data = pd.DataFrame(new_data)
