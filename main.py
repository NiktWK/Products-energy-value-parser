import requests, json, csv, pandas as pd, xlsxwriter
from pandas.io.excel import ExcelWriter
from bs4 import BeautifulSoup
from head import DATA_PATH
from head import url
from head import headers

def saveSRC(src, filename):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(src)

def readSRC(filename):
    with open(filename, encoding="utf-8") as file:
        src = file.read()
    return src

request = requests.get(url, headers = headers)
src = request.text
soup = BeautifulSoup(src, "lxml")

uls = soup.find_all('ul', class_ = "product")[:-1]
all_categories_links =  {}
count = 0

try:
    file = open('products.py')
except IOError as e:
    print(u'Please, create the xlsx file')
    exit()
else:
    file.close()

for ul in uls:
    links = ul.find_all("a")

    for item in links:
        link_text = item.text
        link = url[:-8] + '/' + item.get("href")
        all_categories_links[link_text] = link

products_parameters = {}
for c_name, c_href in all_categories_links.items():
    rep = [" ", "-", ",", "'"]

    for sign in rep:
        if sign in c_name:
            c_name = c_name.replace(sign, '_')
            
    req = requests.get(url = c_href, headers = headers)
    
    saveSRC(req.text, f"{DATA_PATH}pages/{count}_{c_name}")
    src = readSRC(f"{DATA_PATH}pages/{count}_{c_name}")

    soup = BeautifulSoup(src, "lxml")

    # Save names of web-table heads
    table_head = soup.find_all("a", class_ = "active")[1:-1]

    # Saving to EXEL-table
    products_names = soup.find_all("td", class_ = "views-field views-field-title active")
    proteins = soup.find_all("td", class_ = "views-field views-field-field-protein-value")
    carbohydrates = soup.find_all("td", class_ = "views-field views-field-field-carbohydrate-value")
    fats = soup.find_all("td", class_ = "views-field views-field-field-fat-value")
    kcals = soup.find_all("td", class_ = "views-field views-field-field-kcal-value")
    data = {
        table_head[0].text: [i.text for i in products_names], 
        table_head[1].text: [float(i.text if i.text != "\n" else 0) for i in proteins],
        table_head[2].text: [float(i.text if i.text != "\n" else 0) for i in fats],
        table_head[3].text: [float(i.text if i.text != "\n" else 0) for i in carbohydrates],
        table_head[4].text: [float(i.text if i.text != "\n" else 0) for i in kcals]
        }

    df = pd.DataFrame(data)
    products_parameters[c_name] = data

    with ExcelWriter(f"{DATA_PATH}products.xlsx", engine = "openpyxl", mode = "a") as writer:
        df.to_excel(writer, sheet_name = c_name, index = False)

    print(f"Module {c_name} was saved   [Left: {len(all_categories_links)-1-count}]")
    count += 1

with open(f"{DATA_PATH}all_products.json", "w", encoding = "utf-8")  as json_file:
    json.dump(products_parameters, json_file, indent = 4, ensure_ascii = False)