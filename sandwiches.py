# coding=utf-8
import requests
from bs4 import BeautifulSoup
import mysql.connector

connection = mysql.connector.connect(host='localhost', database='12team', user='root', password='')
cur = connection.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS sandwiches (
  id INT,
  name TEXT,  
  link TEXT, 
  kcal INT,
  recipe TEXT,
  formula TEXT,
  portions INT
)''')
s = []
portions = []
form = []
kcal = []
recipe = []
link = []
link_img = []
url = 'https://calorizator.ru/recipes/category/sandwiches'
page = requests.get(url)
soup = BeautifulSoup(page.text, 'lxml')
contents_name = soup.find_all('td', class_="views-field views-field-title active")
contents_kcal = soup.find_all('td', class_="views-field views-field-field-kcal-value")
for j in range(len(contents_kcal)):
    kcal.append(contents_kcal[j].text)
for i in range(len(contents_name)):
    link.append(contents_name[i].find('a').get('href'))
    if contents_name[i].find('a') is not None:
        recipe.append(contents_name[i].text)
for i in range(1, 5):
    url = 'https://calorizator.ru/recipes/category/sandwiches?page='+str(i)
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml')
    contents_name = soup.find_all('td', class_="views-field views-field-title active")
    contents_kcal = soup.find_all('td', class_="views-field views-field-field-kcal-value")
    for j in range(len(contents_kcal)):
        kcal.append(contents_kcal[j].text)
    for j in range(len(contents_name)):
        link.append(contents_name[j].find('a').get('href'))
        if contents_name[j].find('a') is not None:
            recipe.append(contents_name[j].text)
for i in range(len(link)):
    s.append(i)
    s[i] = ''
    form.append(i)
    form[i] = ''
    url = 'https://calorizator.ru' + str(link[i])
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml')
    link_img.append(soup.find('img').get('src'))
    portions.append(int(soup.find('span', itemprop='recipeYield').text))
    recipe_text_1 = soup.find_all('li', class_="recipe-ingr-item")
    for j in range(len(recipe_text_1)):
        s[i] = s[i] + recipe_text_1[j].text + '  '
    recipe_text_1 = soup.find_all('li', class_="recipes-ingr-item")
    for j in range(len(recipe_text_1)):
        s[i] = s[i] + recipe_text_1[j].text + '  '
    formula_1 = soup.find_all('div', class_='field-item odd')
    for j in range(len(formula_1)):
        if formula_1[j].find('ol') is not None:
            if formula_1[j].find('li') is not None:
                form[i] = form[i] + formula_1[j].text + '  '
for i in range(len(recipe)):
    kcal[i] = int(kcal[i])
    lip = (i, recipe[i], link_img[i], kcal[i], s[i], form[i], portions[i])
    cur.execute('INSERT INTO sandwiches VALUES( %s, %s, %s, %s, %s, %s, %s);', lip)
    connection.commit()
