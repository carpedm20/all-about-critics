class Critic(object):
    def __init__(self, name, link):
        self.name = name
        self.link = link
        self.reviews = []
    
    def __repr__(self):
        msg = '<Critic %s (%s): %s>' % (self.name, self.link, len(self.reviews))
        return msg.encode('utf8')

class Movie(object):
    def __init__(self, mid, title):
        self.mid = mid
        self.title = title
        self._title_en = ""
        self._time = None
        
    @property
    def link(self):
        return "http://www.cine21.com/movie/info/movie_id/" + str(self.mid)
    
    @property
    def time(self):
        if not self._time:
            self.get_info()
        
        return self._time
    
    @property
    def title_en(self):
        if not self._title_en:
            self.get_info()
        
        return self._title_en
    
    def get_info(self):
        soup = get_soup(self.link)
        self._title_en = soup.select(".tbl_basic3 tr td")[0].text.strip()

        date = soup.select(".tbl_basic3 tr td")[-1].text.strip()
        self._time = time.strptime(date, "%Y-%M-%d")
        
    def get_imdb(self):
        if not self._title_en or not self._time:
            self.get_info()

        movies = imdb.find_by_title(self._title_en)
        print movies
        
        for movie in movies:
            if int(movie['year']) == self.time.tm_year:
                print movie
        
    def __repr__(self):
        msg = '<Movie %s (%s)>' % (self.title, self.link)
        return msg.encode('utf8')
        
class Review(object):
    def __init__(self, movie, text, rating):
        self.movie = movie
        self.text = text
        self.rating = rating
    
    def __repr__(self):
        msg = '<Review %s (%s)>' % (self.movie.title, self.rating)
        return msg.encode('utf8')
