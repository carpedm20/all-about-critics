class Critic(object):
    def __init__(self, name, link):
        self.name = name
        self.link = link
        self.reviews = []

class Movie(object):
    def __init__(self, mid, link, title):
        self.mid = mid
        self.link = link
        self.title = title
        
class Review(object):
    def __init__(self, movie, text, rating):
        self.movie = movie
        self.text = text
        self.rating = rating
