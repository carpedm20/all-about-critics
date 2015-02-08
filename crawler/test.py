import pickle

with open('critics.pkl','rb') as f:
    critics = pickle.load(f)
with open('movies.pkl','rb') as f:
    movies = pickle.load(f)
