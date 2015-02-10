import json
from glob import glob

data = []

for fname in ['critic-0.jsonlines']+glob('*new*.jsonlines'):
    print fname
    with open(fname) as f:
        for line in f:
            data.append(json.loads(line))

new_data = []
for i in data:
    if i['imdb_mid'] != -1:
        new_data.append(i)

with open('compact.json','w') as f:
    json.dump(new_data, f)
