from difflib import SequenceMatcher as sm

def is_same_name(a,b):
    for (x,y) in [(a,b),(b,a)]:
        for word in x.split():
            if word in y:
                return True
    if sm(a=list(set(b)), b=list(set(a))).ratio() > 0.7:
        return True
    return False

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
        self._title_en = None
        self._year = None
        self._time = None
        self._director = None
        self._director_en = None
        self._naver_mid = None
        self._imdb_mid = None
        self._imdb_candidates = []
        
        self._ko_user_star = None
        self._ko_critic_star = None
        self._fo_user_star = None
        self._fo_critic_star = None
        
    @property
    def link(self):
        return "http://www.cine21.com/movie/info/movie_id/" + str(self.mid)
    
    @property
    def director(self):
        if not self._director: self.get_info()
        return self._director
    
    @property
    def director_en(self):
        if not self._director_en: self.get_info()
        return self._director_en
    
    @property
    def time(self):
        if not self._time: self.get_info()
        return self._time
    
    @property
    def year(self):
        if not self._year: self.get_info()
        return self._year
    
    @property
    def title_en(self):
        if not self._title_en: self.get_info()
        return self._title_en
    
    @property
    def naver_mid(self):
        if not self._naver_mid: self.get_naver()
        return self._naver_mid
    
    @property
    def imdb_mid(self):
        if not self._imdb_mid: self.get_imdb()
        return self._imdb_mid
    
    def get_info(self):
        try:
            soup = get_soup(self.link)
            h3 = soup.select(".desc h3")[0].text.strip()
            self._year = int(re.findall(r'\(\d\d\d\d\)$', h3)[-1][1:-1])

            tds = soup.select(".tbl_basic3 tr td")

            self._title_en = tds[0].text.strip()
            self._director = tds[1].text.strip()

            try:
                soup = get_soup(CINE + tds[1].a['href'])
            except:
                soup = get_soup(CINE + tds[2].a['href'])

            try:
                self._director_en = re.findall(r'\(.*\)$', soup.select("span.name")[0].text.strip())[-1][1:-1]
            except:
                return False
            try:
                self._time = time.strptime(tds[-1].text.strip(), "%Y-%M-%d")
            except:
                return False
        except:
            return False
            
    def get_naver(self):
        query = urllib.urlencode({'q' : self.title.encode('utf-8')})
        
        body = requests.get(NAVER_AUTO + query).text
        j = json.loads(body[body.find('{'):body.rfind('}')+1])
        
        ans = None
        
        if len(j['items']) > 2:
            for item in j['items']:
                if item:
                    if not self._time: self.get_info()
                    if self._time == time.strptime(item[0][1][0], "%Y%M%d") and item[0][1][-1] == "movie":
                        ans = item
                        break
        else:
            ans = j['items'][0]
        
        if not ans:
            if self.mid == 27710:
                self._naver_mid = 71424
                return
            elif self.mid == 26369:
                self._naver_mid = 49475
                return
            elif self.mid == 23105:
                self._naver_mid = 64920
                return
            elif self.mid == 3684:
                self._naver_mid = 3470449
                return
            raise Exception(" [!] NAVER Movie not found : %s" % self.mid)
            
        self._naver_mid = ans[0][-2][0]
            
        #soup = get_soup(NAVER_INFO+self._naver_mid)
        
        
    def get_imdb(self):
        if not self._title_en or not self._time or not self._year:
            self.get_info()

        try:
            movies = imdb.find_by_title(self._title_en)
        except:
            movies = imdb.find_by_title(self._title_en.encode('utf-8'))
        ans = None
        
        if len(movies) > 1:
            self._imdb_candidates = []
            candidates = []
            
            for movie in movies:
                if movie['year']:
                    year = int(movie['year'])
                    
                    if year == self._year or year == self.time.tm_year:
                        candidates.append(movie)

            if len(candidates) == 0:
                candidates = movies

            for candidate in candidates:
                info = imdb.find_movie_by_id(candidate['imdb_id'])

                is_possible = False
                for director in info.directors_summary:
                    if is_same_name(director.name, self._director_en):
                        self._imdb_candidates.append(candidate)
                        break

            if len(self._imdb_candidates) > 1:
                ans = self._imdb_candidates[0]
                max_gap = self.year - int(ans['year'])
                
                for candidate in self._imdb_candidates[1:]:
                    if max_gap > self.year - int(candidate['year']):
                        ans = candidate
                
                self._imdb_mid = ans['imdb_id']
                return
            
                #raise Exception("Too many candidates : %s" % self._imdb_candidates)

                #soup = get_soup("http://www.imdb.com/title/%s/releaseinfo" % candidate['imdb_id'])
                #for tr in soup.select("#release_dates tr"):
                #    if tr.find("a").text == "South Korea":
                #        pass
                    
            if len(self._imdb_candidates) == 1:
                ans = self._imdb_candidates[0]
            elif len(self._imdb_candidates) == 0:
                self._imdb_mid = -1
                return
            else:
                raise Exception (" [!] IMDB Movie not found : %s" % len(self._imdb_candidates))
        elif len(movies) == 0:
            return False
        else:
            ans = movies[0]
        
        if not ans:
            raise Exception (" [!] IMDB Movie not found")
            
        self._imdb_mid = ans['imdb_id']
        
    def __repr__(self):
        msg = '<Movie %s<%s> ( %s )>' % (self.title, self.mid, self.link)
        return msg.encode('utf8')
        
class Review(object):
    def __init__(self, movie, text, rating):
        self.movie = movie
        self.text = text
        self.rating = rating
    
    def __repr__(self):
        msg = '<Review %s (%s)>' % (self.movie.title, self.rating)
        return msg.encode('utf8')

def find_movie(movies, mid):
    for movie in movies:
        if movie.mid == mid:
            return movie
