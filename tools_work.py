import os
from flask import request

list_simbols_title = ['<', '>', "*", "/", '|', ':', '\\', '"']
list_simbols_text = ['<']


def replace_simbols_title(string):
    for simbol in list_simbols_title:
        string = string.replace(simbol, '')
    string = string.replace('?', '#')
    return string


def replace_simbols_text(string):
    for simbol in list_simbols_text:
        string = string.replace(simbol, '')
    string = string.replace('\r','')
    return string


class Reply:
    def __init__(self, text, article_title):
        self.data = text[:19]
        self.identification = text[20:56]
        with open(os.path.join('articles', article_title, text), 'r', encoding='utf-8') as file:
            data = file.read()
        self.text = data


def identification_to_color(identification):
    list_int = [int(x) for x in identification if x.isdigit()]
    list_int = list_int[:3]
    if len(list_int) < 3:
        list_int = [0, 0, 0]
    return list_int


def remove_char(i, string):
    if i<len(string)-2:
        return string[:i] + string[i + 1:]
    return string


def open_reply(text, article_title):
    with open(os.path.join('articles', article_title, text), 'r', encoding='utf-8') as file:
        data = file.read()

    for row in data.split('\n'):
        if '>>' in row:
            data = data.replace(row, '<a style="color: rgb(174 220 174);">'+row+'</a>')


    list_int = identification_to_color(text[20:56])

    return {'date': text[:19],
            'identification': text[20:56],
            'text': data,
            'reply': [],
            'replies': [],
            'color': f'max-width: 500px; margin-left: auto; margin-right: auto; background-color: rgb({str(45 + list_int[0])} {str(45 + list_int[1])} {str(45 + list_int[2])});'}


class Article:
    def __init__(self, text):
        self.date = text[:19]
        self.title = text[56:].replace('#', '?')
        self.id = f'view?id={text[20:56]}'
        try:
            with open(os.path.join('articles', text, 'article.txt'),  encoding='utf-8') as file:
                data = file.read()
            self.text = data
        except Exception as e:
            self.text = str(e)
        self.count_reply = len(os.listdir(os.path.join('articles', text))) - 2
        list_int = identification_to_color(text[20:56])
        self.css = f'max-width: 500px; margin-left: auto; margin-right: auto; background-color: rgb({str(45 + list_int[0])} {str(45 + list_int[1])} {str(45 + list_int[2])});'


def write_reply(directory, name_file, text):
    name_file = name_file.replace(':', '-')
    with open(os.path.join(directory, name_file), 'w', encoding='utf-8') as f:
        f.write(text)


def get_ip():
    ip = 'None'
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        ip = request.environ['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.environ['REMOTE_ADDR']
    return ip
