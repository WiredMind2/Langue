import requests
import re
import csv
from bs4 import BeautifulSoup, element

wikipedia_urls = [
    "https://en.wiktionary.org/wiki/Appendix:JLPT/N1",
    "https://en.wiktionary.org/wiki/Appendix:JLPT/N2",
    "https://en.wiktionary.org/wiki/Appendix:JLPT/N3",
    "https://en.wiktionary.org/wiki/Appendix:JLPT/N4",
    "https://en.wiktionary.org/wiki/Appendix:JLPT/N5",
    "https://en.wiktionary.org/wiki/Appendix:1000_Japanese_basic_words",
]

csv_files = [
    "vocabulary_65001.csv",
    "vocabulary_65002.csv",
    "vocabulary_65003.csv",
    "vocabulary_65004.csv",
    "vocabulary_65005.csv",
]
db_file = "JLPT_N1.csv"


def wikipedia_parser(urls):
    for url in urls:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        main = soup.find("div", class_="mw-parser-output")

        for elem in main.find_all('ul', recursive=False):
            for line in elem.find_all('li'):
                if len(line.contents) >= 2:
                    jpn = []
                    for span in line.find_all('span'):
                        jpn.append(span.string)
                    if not jpn:
                        continue
                    lastSpan = [i for i, e in enumerate(line.contents) if e.name == "span"][-1]
                    eng = ''.join(list(line.strings)[lastSpan + 1:])
                    eng = re.sub(r". *[-–] *", "", eng)
                    eng = re.sub(r"[\(\[][^\(\)\[\]]+[\)\]]", "", eng)
                    eng = eng.strip()
                    yield {'eng': eng, 'jpn': jpn}
                    # db.writerow([eng] + jpn)


def csv_merger(files):
    for file in files:
        with open(file, 'r', encoding="utf-8") as f:
            reader = csv.reader(f)
            for line in reader:
                print({'eng': line[2], 'jpn': line[0:1]})
                yield {'eng': line[2], 'jpn': line[0:1]}


with open(db_file, 'w', encoding="utf-8") as f:
    db = csv.writer(f, delimiter=";")
    for line in wikipedia_parser(wikipedia_urls):
        db.writerow([line['eng']] + line['jpn'])

    for line in csv_merger(csv_files):
        db.writerow([line['eng']] + line['jpn'])