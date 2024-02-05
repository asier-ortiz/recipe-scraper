from bs4 import BeautifulSoup
import json
import re
import requests
import xmltodict

site_map = xmltodict.parse(requests.get('https://www.hogarmania.com/sitemap.cocina-hogarmania.xml').text)
urls = [url['loc'] for url in site_map['urlset']['url']]
filtered_urls = [u for u in urls if u.startswith('https://www.hogarmania.com/cocina/recetas/')]
data = []


def scrap_recipe_data(url):
    result = requests.get(url)
    content = result.content
    soup = BeautifulSoup(content, 'html.parser')

    category = ''
    try:
        category = soup.find('div', class_='cab-destacado').findChild('p').text
    except:
        pass

    title = ''
    try:
        title = soup.find('h1', class_='m-titulo').text
    except:
        pass

    prep_time = ''
    try:
        prep_time = soup.find('span', text=re.compile('Tiempo total:')).next_sibling.text
    except:
        pass

    servings = ''
    try:
        h2_text = soup.find('h2', id=re.compile('^ingredientes-personas')).text
        servings = re.search(r'\d+', h2_text).group()
    except:
        pass

    img_url = ''
    try:
        img_url = "https://www.hogarmania.com" + \
                  soup.find('div', class_='print_video').findChild('img', class_='img-responsive')['src']
    except:
        pass

    ingredients = []
    try:
        for li in soup.find('ul', class_='ingredientes').find_all('li'):
            ingredients.append(li.text)
    except:
        pass

    instructions = []
    try:
        for el in soup.find('h2', text=re.compile('^E')).next_siblings:
            if el.name == 'h2':
                break
            elif el.name == 'p' and el.next_element.name == 'strong' and el.next_element.text == 'Consejo':
                break
            elif el.name == 'p':
                if el.text != '':
                    instructions.append(el.text)
    except:
        pass

    data.append(
        {
            'category': category,
            'title': title,
            'prepTime': prep_time,
            'servings': int(servings),
            'img': img_url,
            'ingredients': ingredients,
            'instructions': instructions,
            'source': url
        }
    )


def write_data_to_json():
    count = 1
    for url in filtered_urls:
        try:
            print('Processing recipe nº ' + str(count))
            scrap_recipe_data(url)
        except:
            continue
        finally:
            count += 1

    with open('recipes.json', 'w', encoding='UTF-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False)

    json_file.close()


if __name__ == "__main__":
    print('Writing ' + str(len(filtered_urls)) + ' recipes, please wait...')
    write_data_to_json()
