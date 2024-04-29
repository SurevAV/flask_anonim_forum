from flask import request, Flask, redirect
from flask import render_template
import uuid
from datetime import datetime
import math
from tools_work import *
import random
import json
import re


app = Flask(__name__)
ip_dict = {}
url_site = 'http://127.0.0.1:8000'
count_articles_on_page = 10

to = re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}', re.I)


def captcha_image(ip):
    path_images_captcha = os.listdir(os.path.join('static', 'images', 'captcha'))
    random_number = random.randint(1, int(len(path_images_captcha) / 2))
    with open(os.path.join('static', 'images', 'captcha', f'{str(random_number)}.txt'), 'r', encoding='utf-8') as file:
        ip_dict[ip] = file.read()
    return f'/static/images/captcha/{random_number}.png'


@app.route("/", methods=["Get", "POST"])
def main_get():
    try:
        page = int(request.args.get('page'))
    except:
        page = 1

    if not request.args.get('panel_input_search') or request.args.get('panel_input_search') == '':
        panel_input_search = ''
    else:
        panel_input_search = request.args.get('panel_input_search')



    filter_articles = os.listdir(os.path.join('articles'))
    panel_input_search_lower = panel_input_search.lower()
    filter_articles = [i for i in filter_articles if panel_input_search_lower in i.lower()]

    filter_articles.sort()
    filter_articles.reverse()

    len_pages = math.ceil(len(filter_articles) / count_articles_on_page)

    page_range = 3
    from_page = page - page_range
    if from_page < 1:
        from_page = 1

    to_page = page + page_range
    if to_page > len_pages:
        to_page = len_pages + 1
    list_pagination = [[f'?panel_input_search={panel_input_search.replace(" ", "+")}&page={str(i)}', str(i)] for i in
                       range(from_page, to_page)]

    articles = [Article(item) for item in filter_articles[(page - 1) * count_articles_on_page
                                                          :(page - 1) * count_articles_on_page
                                                           + count_articles_on_page]]



    article_title = ''
    article_text = ''

    ip = get_ip()

    with open(os.path.join('main.txt'), 'r', encoding='utf-8') as file:
        main_text = file.read()


    if request.method == 'POST':
        if ip_dict.get(ip) and ip_dict[ip] == request.form['panel_input_captcha']:

            if request.form['title_input'] and replace_simbols_title(request.form['title_input']) != '' and len(
                    request.form['title_input']) < 193:
                title = request.form['title_input']
                identification = str(uuid.uuid4())
                title = f'{str(datetime.now())[:19]} {identification} {title}'
                name_dir = os.path.join('articles', replace_simbols_title(title.replace(':', '-')))
                for i in range(192):
                    if name_dir[-1] == ' ':
                        name_dir = name_dir[:-1]
                    else:
                        break

                os.makedirs(name_dir)
                write_reply(name_dir, 'article.txt', replace_simbols_text(request.form['text_input']))
                write_reply(name_dir, 'ip.txt', ip)

                return redirect(f'/view?id={identification}')


        else:
            return render_template("main.html",
                                   captcha_image=captcha_image(ip),
                                   article_title=request.form['title_input'],
                                   article_text=request.form['text_input'],
                                   captcha_text='Неправильно введена капча',
                                   articles=articles,
                                   list_pagination=list_pagination,
                                   page=str(page),
                                   main_text=main_text)

    return render_template("main.html",
                           captcha_image=captcha_image(ip),
                           article_title=article_title,
                           article_text=article_text,
                           captcha_text='Капча',
                           articles=articles,
                           list_pagination=list_pagination,
                           page=str(page),
                           main_text=main_text)


@app.route("/view", methods=["Get", "POST"])
def view():


    identification = request.args.get('id')
    url = f'{url_site}/get?identification={identification}'
    identification = identification.lower()
    articles = os.listdir(os.path.join('articles'))

    article_title = [i for i in articles if identification == i[20:56].lower()][0]
    article = Article(article_title)

    answer_text = ''
    ip = get_ip()

    if request.method == 'POST':
        if ip_dict.get(ip) and ip_dict[ip] == request.form['panel_input_captcha']:

            file_name = f'{str(datetime.now())[:19]} {str(uuid.uuid4())} {ip}.txt'
            name_dir = os.path.join('articles', article_title)

            write_reply(name_dir, file_name, replace_simbols_text(request.form['text_input'][:5000]))
        else:
            return render_template("view.html",
                                   captcha_image=captcha_image(ip),
                                   reply_text=answer_text,
                                   captcha_text='Неправильно введена капча',
                                   article=article,
                                   url=url
                                   )
        return render_template("view.html",
                               captcha_image=captcha_image(ip),
                               reply_text=answer_text,
                               captcha_text='Капча',
                               article=article,
                               url=url
                               )


    return render_template("view.html",
                           captcha_image=captcha_image(ip),
                           reply_text=answer_text,
                           captcha_text='Капча',
                           article=article,
                           url=url
                           )


@app.route("/get", methods=["Get"])
def get():
    identification = request.args.get('identification')
    identification = identification.lower()
    articles = os.listdir(os.path.join('articles'))
    article_title = [i for i in articles if identification == i[20:56].lower()][0]
    replies_list = os.listdir(os.path.join('articles', article_title))
    replies_list.sort()

    replies_list = [open_reply(i, article_title) for i in replies_list[:-2]]


    for reply in replies_list:
        for identification_reply in to.findall(reply['text'])[:50]:
            reply['text'] = reply['text'].replace(identification_reply, '')
            reply['reply'].append(identification_reply)

            for reply_change in replies_list:
                if reply_change['identification'] == identification_reply:
                    reply_change['replies'].append(reply['identification'])

    return json.dumps(replies_list)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
