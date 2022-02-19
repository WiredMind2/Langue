from tkinter import *
import pykakasi
import xml.etree.ElementTree as ET
import random
import difflib
import csv

# 0x3041 - 0x3096 - Hiragana
# 0x30A0 - 0x30FF - Katakana


kks = pykakasi.kakasi()


class Char_Data:
    def __init__(self):
        self.hiraganas = [chr(i) for i in range(0x3040, 0x309F)]
        self.katakanas = [chr(i) for i in range(0x30A0, 0x30FF)]

        self.hira_to_kata = dict(zip(self.hiraganas, self.katakanas))
        self.kata_to_hira = dict(zip(self.katakanas, self.hiraganas))

        self.hiraganas_table = (
            (['あ'], ['い'], ['う'], ['え'], ['お']),
            (['か', 'が'], ['き', 'ぎ'], ['く', 'ぐ'], ['け', 'げ'], ['こ', 'ご']),
            (['さ', 'ざ'], ['し', 'じ'], ['す', 'ず'], ['せ', 'ぜ'], ['そ', 'ぞ']),
            (['た', 'だ'], ['ち', 'ぢ'], ['つ', 'づ'], ['て', 'で'], ['と', 'ど']),
            (['な'], ['に'], ['ぬ'], ['ね'], ['の']),
            (['は', 'ば', 'ぱ'], ['ひ', 'び', 'ぴ'], ['ふ', 'ぶ', 'ぷ'], ['へ', 'べ', 'ぺ'], ['ほ', 'ぼ', 'ぽ']),
            (['ま'], ['み'], ['む'], ['め'], ['も']),
            (['や'], [None], ['ゆ'], [None], ['よ']),
            (['ら'], ['り'], ['る'], ['れ'], ['ろ']),
            (['わ'], [None], [None], [None], ['を']),
            (['ん'], [None], [None], [None], [None],)
        )

        self.hiraganas_small = {
            'ぁ': 'あ',
            'ぃ': 'い',
            'ぅ': 'う',
            'ぇ': 'え',
            'ぉ': 'お',
            'っ': 'つ',
            'ゃ': 'や',
            'ゅ': 'ゆ',
            'ょ': 'よ',
            'ゎ': 'わ',
            'ゕ': 'か',
            'ゖ': 'け'
        }

        self.katakanas_table = [[[self.convert_char(char, to_katakana=True) for char in cell] for cell in line] for line in self.hiraganas_table]

        self.katakanas_small = dict((self.convert_char(a, to_katakana=True), self.convert_char(b, to_katakana=True)) for a, b in list(self.hiraganas_small.items()))

    def convert_char(self, chars, to_katakana=None):
        if not chars:
            return
        out = ""
        if to_katakana is None:
            to_katakana = not self.hiragana_mode
        for char in chars:
            if to_katakana:
                out += self.hira_to_kata.get(char, char)
            else:
                out += self.kata_to_hira.get(char, char)
        return out

    def know_chars(self, chars):
        known = set(self.hiraganas) | set(self.katakanas) | {' ', '"'}
        for char in chars:
            if char not in known:
                # print("Unknown char: " + char + " in string: " + chars)
                return False
        return True


class Hira_Tester(Char_Data):
    def __init__(self):
        super().__init__()
        # self.get_db()
        restarted = hasattr(self, "fen")

        if not restarted:
            self.question = None
            self.answer = None
            self.hiragana_mode = False  # True for self.hiraganas, False for self.katakanas
            self.change_char("HIRAGANA", reload=False)()
            self.force_use = {}
            self.learned_treshold = 5  # How many times you must write a char correctly before removing it from force_use

        self.font = ("Arial", 20)
        self.but_font = ("Arial", 15)
        self.help_font = ("Arial", 18)

        self.bg_a = "#AAAAAA"
        self.bg_b = "#DDDDDD"
        self.fg = "#000000"

        if restarted:
            for w in self.fen.winfo_children():
                w.destroy()
        else:
            self.fen = Tk()
        self.fen.configure(bg=self.bg_a)
        self.fen.minsize(1500, 500)
        main = Frame(self.fen, bg=self.bg_a)
        if True:
            main.grid_columnconfigure(0, weight=1)

            if restarted:
                self.question_var.set(self.convert_char(self.question))
            else:
                self.question_var = StringVar()
                self.question_var.set("Hiraganas here")
            self.in_lbl = Label(
                main,
                textvariable=self.question_var,
                font=self.font,
                bg=self.bg_b,
                fg=self.fg)
            self.in_lbl.grid(
                row=0,
                column=0,
                sticky="nsew")

            Label(
                main,
                text="=",
                font=self.font,
                bg=self.bg_a,
                fg=self.fg
            ).grid(row=0, column=1, padx=10)

            self.out_var = StringVar()
            self.out_var.set("")
            self.out_ent = Entry(
                main,
                textvariable=self.out_var,
                font=self.font,
                bg=self.bg_b,
                fg=self.fg,
                relief="flat",
                width=20)
            self.out_ent.grid(
                row=0,
                column=2,
                padx=(0, 10))
            self.out_ent.bind("<Return>", self.validate)

            self.ok_but = Button(
                main,
                text="Validate",
                font=self.but_font,
                bg=self.bg_b,
                fg=self.fg,
                command=self.validate)
            self.ok_but.grid(
                row=0,
                column=3)

            self.next_but = Button(
                main,
                text="Next",
                font=self.but_font,
                bg=self.bg_b,
                fg=self.fg,
                command=self.get_question)
            self.next_but.grid(
                row=0,
                column=4)

            self.help_but = Button(
                main,
                text="Help",
                font=self.but_font,
                bg=self.bg_b,
                fg=self.fg,
                command=self.help)
            self.help_but.grid(
                row=0,
                column=5)

        info_frame = Frame(main, bg=self.bg_a)
        if True:
            info_frame.grid_columnconfigure(0, weight=1)
            self.info_var = StringVar()
            Label(
                info_frame,
                textvariable=self.info_var,
                font=self.but_font,
                bg=self.bg_b,
                fg=self.fg
            ).grid(
                row=0, column=0, sticky="nsew"
            )
            info_frame.grid(row=1, column=0, columnspan=1, sticky="nsew", pady=5)

        # __________________________________________

        use_frame = Frame(self.fen, bg=self.bg_a)
        if True:
            use_frame.grid_columnconfigure(0, weight=1)
            char_frame = Frame(use_frame, bg=self.bg_a)
            [char_frame.grid_columnconfigure(i, weight=1) for i in range(2)]
            Button(
                char_frame,
                text="Use hiragana",
                font=self.but_font,
                bg=self.bg_b,
                fg=self.fg,
                width=20,
                command=self.change_char("HIRAGANA")
            ).grid(
                row=0,
                column=0,
                sticky="nsew"
            )
            Button(
                char_frame,
                text="Use katakana",
                font=self.but_font,
                bg=self.bg_b,
                fg=self.fg,
                width=20,
                command=self.change_char("KATAKANA")
            ).grid(
                row=0,
                column=1,
                sticky="nsew"
            )
            char_frame.grid(row=0, column=0, sticky="nsew")

        # __________________________________________

        type_frame = Frame(use_frame, bg=self.bg_a)
        if True:
            self.cats = ("dakutens", "handakutens")
            for i, cat in enumerate(self.cats):
                type_frame.grid_columnconfigure(i, weight=1)
                setattr(self, "use_" + cat, True)
                b = Button(
                    type_frame,
                    text="Using " + cat,
                    font=self.but_font,
                    bg=self.bg_b,
                    fg=self.fg,
                    width=20
                )
                b.configure(command=lambda cat=cat, b=b: self.switch_cat(cat, b))
                b.grid(row=0, column=i, sticky="nsew")
            type_frame.grid(row=1, column=0, sticky="nsew")

        # ___________________________________________

        help_frame = Frame(self.fen, bg=self.bg_a)
        if True:
            [help_frame.grid_columnconfigure(i, weight=1) for i in range(2)]
            cols = 5

            char_table_frame = Frame(help_frame, bg=self.bg_a)
            [char_table_frame.grid_columnconfigure(i, weight=1) for i in range(cols)]
            for i, line in enumerate(self.chars_table):
                for j, chars in enumerate(line):
                    char = chars[0]
                    self.create_help_cell(char_table_frame, char, i, j)

            dakuten_frame = Frame(help_frame, bg=self.bg_a)
            [dakuten_frame.grid_columnconfigure(i, weight=1) for i in range(cols)]
            for i, char in enumerate(chars[1] for line in self.chars_table for chars in line if len(chars) >= 2):
                self.create_help_cell(dakuten_frame, char, i // cols, i % cols)

            handakuten_frame = Frame(help_frame, bg=self.bg_a)
            [handakuten_frame.grid_columnconfigure(i, weight=1) for i in range(cols)]
            for i, char in enumerate(chars[2] for line in self.chars_table for chars in line if len(chars) >= 3):
                self.create_help_cell(handakuten_frame, char, 0, i)

            force_use_frame = Frame(help_frame, bg=self.bg_a)
            force_use_frame.grid_rowconfigure(1, weight=1)

            Label(
                force_use_frame,
                text="Force use:",
                font=self.font,
                bg=self.bg_b,
                fg=self.fg
            ).grid(
                row=0,
                column=0,
                sticky="nsew",
                pady=2
            )

            self.force_use_sub_frame = Frame(force_use_frame, bg=self.bg_a)
            [self.force_use_sub_frame.grid_columnconfigure(i, weight=1) for i in range(cols)]
            self.draw_force_use_frame()
            self.force_use_sub_frame.grid(row=1, column=0, sticky="nsew")

            char_table_frame.grid(row=0, column=0, rowspan=3, padx=20, ipadx=1, ipady=1, sticky="nsew")
            dakuten_frame.grid(row=0, column=1, padx=20, pady=20, ipadx=1, ipady=1, sticky="nsew")
            handakuten_frame.grid(row=1, column=1, padx=20, pady=20, ipadx=1, ipady=1, sticky="nsew")
            force_use_frame.grid(row=2, column=1, padx=20, pady=20, ipadx=1, ipady=1, sticky="nsew")

        main.grid(row=0, column=0, pady=20, padx=20, sticky="nsew")
        use_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        help_frame.grid(row=2, column=0, sticky="nsew")

        self.fen.grid_rowconfigure(2, weight=1)
        self.fen.grid_columnconfigure(0, weight=1)
        if not restarted:
            self.get_question()

            self.fen.mainloop()

    def create_help_cell(self, parent, char, row, column):
        cell = Frame(parent, bg=self.bg_b)  # , highlightthickness=1, highlightbackground="black")
        cell.grid_columnconfigure(0, weight=1)
        cell.grid_rowconfigure(0, weight=1)
        if char is None:
            return

        roma = kks.convert(char)[0]['hepburn']
        lbl1 = Label(
            cell,
            text=char,
            font=self.help_font,
            bg=self.bg_b,
            fg=self.fg
        )
        lbl1.bind("<Button-1>", lambda e, char=char: self.add_force_use(char))
        lbl1.grid(
            row=0,
            column=0,
            sticky="nsw"
        )
        lbl2 = Label(
            cell,
            text=roma,
            font=self.help_font,
            bg=self.bg_b,
            fg=self.fg
        )
        lbl2.bind("<Button-1>", lambda e, char=char: self.add_force_use(char))
        lbl2.grid(
            row=0,
            column=1,
            sticky="nse"
        )
        cell.bind("<Button-1>", lambda e, char=char: self.add_force_use(char))
        cell.grid(
            row=row,
            column=column,
            sticky="nsew",
            ipadx=15,
            ipady=2,
            padx=1,
            pady=1
        )

    def switch_cat(self, cat, b=None):
        if cat in self.cats:
            attr = "use_" + cat
        current = getattr(self, attr)
        setattr(self, attr, not current)
        if b is not None:
            b.configure(text=("Using " if not current else "Not using ") + cat)

    def csv_parser(self, string):
        in_quote = False
        field = ""
        for letter in string:
            if letter == '"':
                in_quote = not in_quote
            elif not in_quote and letter == ";":
                yield field
                field = ""
            elif letter not in ("\n"):
                field += letter
        yield field

    def get_db_item(self):
        path = "C:/Users/willi/Documents/Python/Langue/JLPT_N1.csv"
        with open(path, 'r', encoding="utf-8", errors='ignore') as f:
            f.seek(0, 2)
            stop = f.tell()
            start = 0
            pos = random.randint(start, stop)
            f.seek(pos)
            f.readline()  # Get to beginning of next line
            line = "\n"
            while line == "\n":
                line = f.readline()
            jpn = list(self.csv_parser(line))
            eng = jpn.pop(0)
            if not jpn:
                #  Probably EOF
                return self.get_db_item()
            return {'eng': eng, 'jpn': jpn}

    def parse_elem(self, e):
        out = {}
        for c in e:
            if len(c) == 0:
                out[c.tag] = c.text
            else:
                out[c.tag] = self.parse_elem(c)
        return out

    def add_force_use(self, char):
        if char in self.force_use:
            self.force_use.pop(char)
        else:
            self.force_use[char] = None
        self.force_use = dict(sorted(self.force_use.items()))
        self.draw_force_use_frame()

    def switch_force_char(self, char):
        value = self.force_use.get(char, "EMPTY")
        if value != "EMPTY":
            if value is None:
                value = 0
            else:
                value = None
            self.force_use[char] = value

        self.draw_force_use_frame()

    def draw_force_use_frame(self):
        cols = 5
        for w in self.force_use_sub_frame.winfo_children():
            w.destroy()
        if len(self.force_use) > 0:
            for i, data in enumerate(self.force_use.items()):
                char, value = data
                cell = Frame(self.force_use_sub_frame, bg=self.bg_b)
                cell.grid_rowconfigure(0, weight=1)
                cell.grid_columnconfigure(0, weight=1)
                self.create_help_cell(cell, char, 0, 0)
                b_text = "🔒" if value is None else str(self.learned_treshold - value).center(3)
                b = Label(
                    cell,
                    text=b_text,
                    font=self.but_font,
                    bg=self.bg_b,
                    fg=self.fg,
                )
                b.bind("<Button-1>", lambda _, char=char: self.switch_force_char(char))
                b.grid(
                    row=0,
                    column=1,
                    sticky="nsw"
                )
                cell.grid(
                    row=i // cols,
                    column=i % cols,
                    sticky="nsew",
                    ipadx=15,
                    ipady=2,
                    padx=1,
                    pady=1
                )
        else:
            Label(
                self.force_use_sub_frame,
                text="Click on a character to add it to the list",
                font=self.but_font,
                bg=self.bg_b,
                fg=self.fg
            ).grid(
                row=0,
                column=0,
                columnspan=cols
            )

    def match_used_cat(self, chars):
        chars = [self.chars_small.get(char, char) for char in chars]
        used = list(chars[0] for line in self.chars_table for chars in line if len(chars) >= 1)
        for i, cat in enumerate(self.cats):
            if getattr(self, "use_" + cat):
                used.extend(chars[i + 1] for line in self.chars_table for chars in line if len(chars) >= i + 2)

        forced_test = any(map(lambda e: e in self.force_use, chars)) if self.force_use else True

        if not used:
            return forced_test
        used_test = all(map(lambda e: e in used, chars))
        return used_test and forced_test

    def get_wrong_character(self, chars_char, answer, ans_chars):
        incorrect_chars = []
        diffs = []
        i = 0
        for diff in difflib.ndiff(chars_char, answer):
            if diff[0] == "-":
                diffs.append(i)
            else:
                if diff[0] == "+":
                    diffs.append(i)
                i += 1

        i = 0
        for ans_char in ans_chars:
            ans_roma = self.get_romaji(ans_char)
            if any(j in diffs for j in range(i, i + len(ans_roma))):
                incorrect_chars.append(self.chars_small.get(ans_char, ans_char))
            i += len(ans_roma)

        return incorrect_chars

    def get_romaji(self, chars):
        if chars is None:
            return None
        out = kks.convert(chars)[0]
        return out['hepburn'].replace("'", "")

    def get_question(self):
        last_question = self.question
        self.question = None

        while self.question is None or self.answer is None or not self.match_used_cat(self.question) or self.question == last_question:
            e = self.get_db_item()
            for chars in e['jpn']:
                if self.know_chars(chars) and self.convert_char(chars) == chars and self.match_used_cat(chars):
                    self.question = chars
                    break

            self.answer = self.get_romaji(self.question)

        self.ok_but.configure(fg=self.fg)

        info = ', '.join(e['jpn']) + ": " + e['eng']
        if len(info) > 70:
            info = info[:65] + "..."
        self.info_var.set(info)
        self.out_var.set("")
        self.question_var.set(self.question)

    def validate(self, *args):
        out = self.out_var.get()
        if out == self.answer:
            self.ok_but.configure(fg="#00FF00")
            self.fen.update_idletasks()

            # update_force_use = False
            for char in self.question:
                if char in self.force_use and self.force_use[char] is not None:
                    if self.force_use[char] >= self.learned_treshold - 1:
                        self.force_use.pop(char)
                        # update_force_use = True
                    else:
                        self.force_use[char] += 1

            self.draw_force_use_frame()

            self.fen.after(1000, self.get_question())
        else:
            wrong_chars = self.get_wrong_character(out, self.answer, self.question)
            for char in wrong_chars:
                self.force_use[char] = 0
            self.force_use = dict(sorted(self.force_use.items()))
            self.draw_force_use_frame()

            self.ok_but.configure(fg="#FF0000")
            self.fen.update_idletasks()
            self.fen.after(1000, lambda: self.ok_but.configure(fg=self.fg))

    def help(self):
        print(self.answer)

    def change_char(self, char, reload=True):
        def handler():
            self.hiragana_mode = char == "HIRAGANA"
            self.chars_table = self.hiraganas_table if self.hiragana_mode else self.katakanas_table
            self.chars_small = self.hiraganas_small if self.hiragana_mode else self.katakanas_small
            if reload:
                self.__init__()
        return handler


if __name__ == "__main__":
    h = Hira_Tester()