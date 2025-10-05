#!/usr/bin/env python3
import curses
import sys
import os

class Buffer:
    def __init__(self, lines=None):
        self.lines = lines if lines else [""]
        self.cx = 0
        self.cy = 0

    def insert(self, ch):
        line = self.lines[self.cy]
        self.lines[self.cy] = line[:self.cx] + ch + line[self.cx:]
        self.cx += 1

    def backspace(self):
        if self.cx > 0:
            line = self.lines[self.cy]
            self.lines[self.cy] = line[:self.cx - 1] + line[self.cx:]
            self.cx -= 1
        elif self.cy > 0:
            prev_line = self.lines[self.cy - 1]
            self.cx = len(prev_line)
            self.lines[self.cy - 1] += self.lines[self.cy]
            del self.lines[self.cy]
            self.cy -= 1

    def newline(self):
        line = self.lines[self.cy]
        self.lines[self.cy] = line[:self.cx]
        self.lines.insert(self.cy + 1, line[self.cx:])
        self.cy += 1
        self.cx = 0

    def move_left(self):
        if self.cx > 0:
            self.cx -= 1
        elif self.cy > 0:
            self.cy -= 1
            self.cx = len(self.lines[self.cy])

    def move_right(self):
        if self.cx < len(self.lines[self.cy]):
            self.cx += 1
        elif self.cy < len(self.lines) - 1:
            self.cy += 1
            self.cx = 0

    def move_up(self):
        if self.cy > 0:
            self.cy -= 1
            self.cx = min(self.cx, len(self.lines[self.cy]))

    def move_down(self):
        if self.cy < len(self.lines) - 1:
            self.cy += 1
            self.cx = min(self.cx, len(self.lines[self.cy]))


def editor(stdscr, fname):
    curses.curs_set(1)
    stdscr.keypad(True)  # important for arrow keys
    curses.raw()
    curses.noecho()

    if os.path.exists(fname):
        with open(fname, "r") as f:
            lines = [l.rstrip("\n") for l in f.readlines()]
    else:
        lines = [""]

    buf = Buffer(lines)
    mode = "NORMAL"

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # draw buffer
        for i, line in enumerate(buf.lines):
            if i < h - 1:
                stdscr.addstr(i, 0, line[:w-1])

        # draw status
        status = f"{fname} -- {mode} -- {buf.cy+1}:{buf.cx+1}"
        stdscr.addstr(h - 1, 0, status[:w-1])

        # move cursor
        scr_y = min(buf.cy, h - 2)
        scr_x = min(buf.cx, w - 2)
        stdscr.move(scr_y, scr_x)
        stdscr.refresh()

        c = stdscr.get_wch()

        if mode == "NORMAL":
            if isinstance(c, str):
                if c == "i":
                    mode = "INSERT"
                elif c == ":":
                    stdscr.addstr(h - 1, 0, ":")
                    curses.echo()
                    cmd = stdscr.getstr(h - 1, 1).decode("utf-8")
                    curses.noecho()
                    if cmd == "wq":
                        with open(fname, "w") as f:
                            f.write("\n".join(buf.lines) + "\n")
                        break
                    elif cmd == "q":
                        break
            else:
                if c == curses.KEY_LEFT:
                    buf.move_left()
                elif c == curses.KEY_RIGHT:
                    buf.move_right()
                elif c == curses.KEY_UP:
                    buf.move_up()
                elif c == curses.KEY_DOWN:
                    buf.move_down()

        elif mode == "INSERT":
            if isinstance(c, str):
                if c == "\x1b":  # ESC
                    mode = "NORMAL"
                elif c == "\n":
                    buf.newline()
                elif c == "\x7f":  # backspace
                    buf.backspace()
                else:
                    buf.insert(c)
            else:
                if c == curses.KEY_BACKSPACE:
                    buf.backspace()


def main():
    if len(sys.argv) < 2:
        print("Usage: ./vi_clone.py <filename>")
        return
    fname = sys.argv[1]
    curses.wrapper(editor, fname)


if __name__ == "__main__":
    main()
