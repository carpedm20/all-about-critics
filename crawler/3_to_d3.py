import json
import pandas as pd

movies = json.loads(open('compact.json').read())
data = json.loads(open('result2.json').read())

movie_dict = dict([(movie['mid'], movie) for movie in movies])

new_data = []
for key, value in data.items():
    m = movie_dict[int(key)]

    value['cine'] = int(key)
    value['director'] = m['director']
    value['director_en'] = m['director_en']
    value['title'] = m['title']
    value['title_en'] = m['title_en']
    value['time'] = m['time']

    new_data.append(value)

data = pd.DataFrame(new_data)
#data = data[data.metacritic.notnull()]

data.poster = data.poster.str.replace('http://movie2.phinf.naver.net/','')
data.poster = data.poster.str.replace('http://movie.phinf.naver.net/','')
data.poster = data.poster.str.replace('/movie_image.jpg\?type=m203_290_2','')

data.to_csv('movie.csv', sep=',', index=False, encoding="utf-8") 

import pickle
with open('critics.pkl','rb') as f:
    critics = pickle.load(f)

new_critics = []
for critic in critics:
    cid = critic.link.split('/')[-1]

    for review in critic.reviews:
        try:
            new_critics.append((cid, review.movie.mid, review.rating, review.text))
        except:
            new_critics.append((cid, review.movie[0].mid, review.rating, review.text))

critics = pd.DataFrame(new_critics, columns=['cid','mid','rating','text'])
#critics = critics[critics.mid.isin(data.cine)]

for i in movie_dict:
    del movie_dict[i]['year']
    try:
        del movie_dict[i]['imdb_candidates']
    except:
        pass

movie_dt = pd.DataFrame(movie_dict)

for movie in movies:
    del movie['director_en']
    del movie['title_en']
    try:
        del movie['imdb_candidates']
    except:
        pass

tmp = pd.DataFrame.from_dict(movies)
del tmp['year']
ans = critics.merge(tmp, on='mid', how='inner').drop_duplicates()

#tmp = tmp.set_index('mid')

#critics = critics.join(tmp, how='outer', on='mid')
#critics = critics[critics.year.notnull()].drop_duplicates()

ans.to_csv('critics.csv', sep=',', index=False, encoding="utf-8")
