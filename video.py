""" Class to represent a youtube video. """

class Video:
    def __init__(self, id, cid, author, title, desc, date):
        self.id = id
        self.cid = cid
        self.author = author
        self.title = title
        self.desc = desc
        self.date = date

    def toJSON(self):
        return [self.id, self.cid, self.author, self.title, self.desc, int(self.date.timestamp())]
