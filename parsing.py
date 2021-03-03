# coding=utf-8
import requests
from bs4 import BeautifulSoup
import mysql.connector


def Create_Table(table):  # создается таблица table с с параметрами (id, name, link, kcal, recipe, formula, portions)
    request = 'CREATE TABLE IF NOT EXISTS ' + str(table) + ' (id INT, name TEXT, link TEXT, kcal INT, recipe TEXT, formula TEXT, portions TEXT)'
    cur.execute(request)


def kcalF():  # функция достаёт со страницы с рецептами калории в каждом блюде и сохраняет в список
    contents_name = soup.find_all('td', class_="views-field views-field-field-kcal-value")
    for i in range(len(contents_name)):
        kcal.append(contents_name[i].text)
    return kcal


def linkF():  # достаёт со страницы категории все ссылки на блюда и сохраняет в список
    contents_name = soup.find_all('td', class_="views-field views-field-title active")
    for i in range(len(contents_name)):
        link.append(contents_name[i].find('a').get('href'))
    return link


def page_count_F():  # функция проверяет есть ли кнопка следующей страницы, если да то возвращает ссылку на нее
    contest_name = soup.find_all('li', class_='pager-next last')
    if not contest_name:
        return None
    else:
        return contest_name[0].find('a').get('href')


def RecipeF():  # функция достает со страницы блюда ингридиенты блюда и пишет их в переменную
    recipe = ''
    contents_name = soup.find_all('li', class_="recipe-ingr-item")  # необходимо искать по обоим тегам, так как на
    # разных страницах блюд разные классы
    for i in range(len(contents_name)):
        recipe = recipe + contents_name[i].text + '  '
    contents_name = soup.find_all('li', class_="recipes-ingr-item")  # необходимо искать по обоим тегам, так как на
    # разных страницах блюд разные классы
    for i in range(len(contents_name)):
        recipe = recipe + contents_name[i].text + '  '
    return recipe


def FormulaF():  # функция достает со страницы блюда его рецепт приготовления
    formula = ''
    contents_name = soup.find_all('div', class_='field-item odd')
    for i in range(len(contents_name)):
        if contents_name[i].find('ol') is not None:
            if contents_name[i].find('li') is not None:
                formula = formula + contents_name[i].text + '  '  # записывается строка с рецептом приготовления
    return formula


def Insert_table(dish, title):  # функция пишет в данную ей таблицу данную строку
    request = 'INSERT INTO ' + dish + ' VALUES( %s, %s, %s, %s, %s, %s, %s);'
    cur.execute(request, title)
    connection.commit()


def soupF(url):  # функция возвращает код страницы
    page = requests.get(url)
    f_soup = BeautifulSoup(page.text, 'lxml')
    return f_soup


def nameF():  # функция выводит название блюда
    return soup.find('h1', id='page-title').text


def portionsF():  # функция выводит количество порций на которое расчитан рецепт
    return soup.find('span', itemprop='recipeYield').text


def link_imgF():  # функция выводит ссылку на фотографию блюда
    return soup.find('img').get('src')


dishes = ['garnish', 'soups', 'sauces', 'desserts', 'cakes', 'salads', 'sandwiches', 'snacks', 'drinks']
# список хранит категории блюд

connection = mysql.connector.connect(host='localhost', database='12team', user='root', password='')
cur = connection.cursor()
# подключаемся к базе данных куда будем все сохранять

for i in dishes:
    link = []
    kcal = []
    Create_Table(i)
    soup = soupF('https://calorizator.ru/recipes/category/' + i)  # возвращаем код страницы из категории i
    while page_count_F() is not None:
        link = linkF()
        kcal = kcalF()
        soup = soupF('https://calorizator.ru' + page_count_F())
    link = linkF()
    kcal = kcalF()
    for j in range(len(link)):  # в цикле проходит по ссылкам на все блюда
        soup = soupF('https://calorizator.ru' + str(link[j]))  # возвращает код страницы определенного блюда
        lip = (j, nameF(), link_imgF(), kcal[j].strip(), RecipeF(), FormulaF(), portionsF())
        # записывает в список необходимые значения блюда
        Insert_table(i, lip)  # записывает lip в необходимую таблицу категории блюда
