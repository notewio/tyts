import ueberzug.lib.v0 as ueberzug
from threading import Thread
import subprocess
import webbrowser
import textwrap
import argparse
import mailcap
import curses
import config
import util
import net
import re


class App:

    @ueberzug.Canvas()
    def main(self, screen, canvas):
        self.screen = screen
        self.canvas = canvas
        self.screen.refresh()

        self.setDimensions()
        self.initUI()
        self.initState()
        self.initLibrary()

        key = ""
        updatePreview = True
        while key != "q":

            if key == "j":
                if self.current < len(self.currentView) - 1:
                    self.current += 1
                    updatePreview = True
                if self.current-self.scroll \
                        > self.video_list_length-self.scroll_padding:
                    self.scroll += 1
            elif key == "k":
                if self.current > 0:
                    self.current -= 1
                    updatePreview = True
                if self.current-self.scroll < self.scroll_padding-1 \
                        and self.scroll > 0:
                    self.scroll -= 1
            elif key == "u":
                self.descScroll += 1
            elif key == "i":
                self.descScroll -= 1
            elif key == "\n":
                self.openVideo()
            elif key == "o":
                webbrowser.open(
                    "https://www.youtube.com/watch?v=" \
                    + self.currentView[self.current].id
                )
            elif key == "/":
                self.searchLibrary()
                updatePreview = True
            elif key == "?":
                self.searchLibrary(regex=True)
                updatePreview = True
            elif key == "r":
                self.updateLibrary()
                updatePreview = True
            elif key == "KEY_RESIZE":
                # TODO: Resizing window does not redraw immediately, only after new key is pressed
                self.setDimensions()
                self.initUI()
                if self.current-self.scroll \
                        > self.video_list_length-self.scroll_padding:
                    self.scroll += self.current-self.scroll \
                                   - self.video_list_length+self.scroll_padding

            if updatePreview:
                self.getThumbnail()
                self.descScroll = 0

            self.drawLeft()
            self.drawRight()

            self.left.refresh()
            self.right.refresh()
            updatePreview = False
            key = screen.getkey()


    def setDimensions(self):
        self.height, self.width = self.screen.getmaxyx()
        self.width_l = int(self.width*0.45)
        self.width_r = self.width - self.width_l

        self.font = util.getFontDimensions()
        self.thumb_height = self.height // 3
        self.thumb_width = int(self.thumb_height * 16/9 * self.font)

        self.video_list_length = (self.height-2) // 2

    def initUI(self):
        self.screen.scrollok(False)
        curses.curs_set(0)
        curses.use_default_colors()
        curses.init_pair(1, -1, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_WHITE, -1)

        self.left = curses.newwin(self.height, self.width_l, 0, 0)
        self.right = curses.newwin(self.height, self.width_r, 0, self.width_l)
        self.thumb = ueberzug.Placement(
            self.canvas, "thumb",
            x=self.width_l+1, y=1,
            width=self.thumb_width, height=self.thumb_height,
            scaler="forced_cover",
            scaling_position_x=0.5, scaling_position_y=0.5
        )

    def initState(self):
        self.current = 0
        self.scroll = 0
        self.scroll_padding = 2
        self.descScroll = 0

    def statusBar(self, window, string, y=0):
        _, width = window.getmaxyx()
        window.insstr(
            y, 0,
            string.ljust(width),
            curses.color_pair(1) | curses.A_BOLD
        )

    def initLibrary(self):
        self.library = config.loadCache()
        self.currentView = self.library[:]
        self.caps = mailcap.getcaps()

    def openVideo(self):
        return subprocess.run(
            mailcap.findmatch(
                self.caps, "video/x-youtube",
                filename="https://www.youtube.com/watch?v=" \
                            + self.currentView[self.current].id
            )[0],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True
        )

    def drawLeft(self):
        self.left.erase()
        self.statusBar(self.left, "Subscriptions")
        self.statusBar(
            self.left,
            "{} in view, {} total".format(
                len(self.currentView),
                len(self.library)
            ),
            self.height-1
        )

        for i in range(0, self.height-2, 2):
            v = i//2 + self.scroll
            if v >= len(self.currentView):
                break
            y = i+1
            vid = self.currentView[v]
            bolded = curses.A_BOLD if v == self.current else 0

            self.left.addnstr(
                y, 0,
                "{} {}".format(
                    ">" if v == self.current else " ", vid.title
                ),
                self.width_l-1,
                bolded
            )

            if y+1 >= self.height-1:
                break
            self.left.addnstr(
                y+1, 4,
                "{} {}".format(
                    vid.date.strftime("%x"), vid.author
                ),
                self.width_l-5,
                curses.color_pair(2) | bolded
            )

    def searchLibrary(self, regex=False):
        curses.curs_set(1)
        curses.echo()

        self.statusBar(self.left, "Search: ", self.height-1)
        self.left.refresh()
        s = self.left.getstr(self.height-1, 8, self.width-8)
        s = s.decode("utf-8")
        if not regex:
            s = s.lower()

        curses.curs_set(0)
        curses.noecho()

        if s == "":
            self.currentView = self.library[:]
        else:
            self.currentView = []
            for vid in self.library:
                if regex:
                    regex = re.compile(s)
                    if regex.search(vid.title) or regex.search(vid.author):
                        self.currentView.append(vid)
                else:
                    if s in vid.title.lower() or s in vid.author.lower():
                        self.currentView.append(vid)

        self.initState()

    def updateLibrary(self):
        channels = config.loadConfig()["channels"]
        for cid in channels:
            author, videos = net.getVideos(cid)
            self.statusBar(self.left, "Loaded " + author, self.height-1)
            self.left.refresh()
            for video in videos:
                util.addToLibrary(self.library, video)
            config.writeCache(self.library)
            self.currentView = self.library[:]
        self.initState()

    def drawRight(self):
        self.right.erase()
        self.statusBar(self.right, "Video Preview")

        if self.current >= len(self.currentView):
            self.statusBar(self.right, "No video to preview", self.height-1)
            return

        vid = self.currentView[self.current]
        self.statusBar(
            self.right,
            "{} // {}".format(vid.id, vid.cid),
            self.height-1
        )

        text_start = self.thumb_height + 2
        self.right.addnstr(
            text_start, 0,
            vid.title,
            self.width_r,
            curses.A_BOLD
        )
        self.right.addnstr(
            text_start+1, 2,
            vid.author,
            self.width_r-2
        )
        self.right.addnstr(
            text_start+2, 2,
            str(vid.date),
            self.width_r-2,
            curses.color_pair(2)
        )

        desc = vid.desc.split("\n")
        wrapped = []
        for line in desc:
            wrapped += textwrap.wrap(line, width=self.width_r-2)
        if self.descScroll < 0:
            self.descScroll = 0
        elif self.descScroll > len(wrapped)-1 > 0:
            self.descScroll = len(wrapped)-1
        for y in range(text_start+4, self.height-1):
            l = y - text_start-4 + self.descScroll
            if l >= len(wrapped):
                break
            self.right.addnstr(
                y, 2,
                wrapped[l],
                self.width_r-2
            )

    def getThumbnail(self):
        if self.current >= len(self.currentView):
            return
        p = Thread(
            target=net.getThumbnail,
            args=(self.currentView[self.current].id, self.thumb)
        )
        p.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Terminal YouTube RSS viewer.")
    parser.add_argument(
        "--create-config", dest="createConfig", action="store_const",
        const=True, default=False,
        help="Create a empty configuration file at $XDG_CONFIG_HOME/tyts/tyts.json"
    )
    args = parser.parse_args()
    if args.createConfig:
        config.createConfig()
    else:
        app = App()
        curses.wrapper(app.main)
