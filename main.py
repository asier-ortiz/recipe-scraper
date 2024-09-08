import re
import requests
import xmltodict
from bs4 import BeautifulSoup
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constantes
SITEMAP_URL = 'https://www.hogarmania.com/sitemap.cocina-hogarmania.xml'
BASE_URL = 'https://www.hogarmania.com'
JSON_OUTPUT_FILE = 'recipes.json'
MAX_THREADS = 10  # Número máximo de hilos concurrentes


def fetch_sitemap(url):
    """Obtener y parsear el sitemap XML, devolviendo URLs filtradas de recetas."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        site_map = xmltodict.parse(response.text)
        urls = [url['loc'] for url in site_map['urlset']['url']]
        return [u for u in urls if u.startswith(f'{BASE_URL}/cocina/recetas/')]
    except requests.RequestException as e:
        logging.error(f"Error al obtener el sitemap: {e}")
        return []


def scrape_recipe_data(url):
    """Extraer datos de recetas desde el contenido HTML."""
    try:
        result = requests.get(url, timeout=10)
        result.raise_for_status()
        soup = BeautifulSoup(result.content, 'html.parser')
    except requests.RequestException as e:
        logging.error(f"Error al obtener la página {url}: {e}")
        return None

    # Extraer título
    title = soup.select_one('h1.m-titulo').get_text(strip=True) if soup.select_one('h1.m-titulo') else ''

    # Extraer categoría (último <li> en la breadcrumb)
    category = ''
    breadcrumb = soup.select('ol.breadcrumb li a')
    if breadcrumb:
        category = breadcrumb[-1].get_text(strip=True)

    # Extraer tiempo de preparación
    prep_time = soup.find('span', text=re.compile('Tiempo total')).next_sibling.get_text(strip=True) if soup.find(
        'span', text=re.compile('Tiempo total')) else ''

    # Extraer porciones
    servings = ''
    try:
        servings_text = soup.find('h2', id=re.compile('^ingredientes-para')).get_text(strip=True)
        servings = int(re.search(r'\d+', servings_text).group())
    except (AttributeError, KeyError, ValueError):
        logging.warning(f"Porciones no encontradas o inválidas para {url}")

    # Extraer URL de imagen principal
    img_url = ''
    try:
        img_tag = soup.find('div', class_='print_video').findChild('img', class_='img-responsive')
        img_url = img_tag['src'] if img_tag and img_tag['src'].startswith('http') else BASE_URL + img_tag['src'] if img_tag else ''
    except (AttributeError, KeyError):
        logging.warning(f"Imagen no encontrada para {url}")

    # Extraer ingredientes
    ingredients = []
    try:
        ingredients = [li.get_text(strip=True) for li in soup.find('ul', class_='ingredientes').find_all('li')]
    except AttributeError:
        logging.warning(f"Ingredientes no encontrados para {url}")

    # Extraer instrucciones (incluyendo imágenes dentro de <p> tags)
    instructions = []
    try:
        instructions_container = soup.select_one('div.articulo')  # Contenedor para instrucciones
        for element in instructions_container.children:
            if element.name == 'p':  # Si es un párrafo, es una instrucción o imagen
                text = element.get_text(strip=True)
                img_tag = element.find('img')
                img_src = img_tag['src'] if img_tag and img_tag['src'].startswith('http') else BASE_URL + img_tag['src'] if img_tag else None

                # Incluir texto y la imagen si está presente
                if text or img_src:
                    instructions.append({'step': text, 'image': img_src})
    except AttributeError:
        logging.warning(f"Instrucciones no encontradas o incompletas para {url}")

    return {
        'category': category,
        'title': title,
        'prepTime': prep_time,
        'servings': servings,
        'img': img_url,
        'ingredients': ingredients,
        'instructions': instructions,
        'source': url
    }


def save_data_to_json(data, filename):
    """Guardar los datos en un archivo JSON sin espacios adicionales."""
    try:
        with open(filename, 'w', encoding='UTF-8') as json_file:
            # Hace que el JSON sea más compacto (sin espacios)
            json.dump(data, json_file, ensure_ascii=False, separators=(',', ':'))
        logging.info(f"Datos guardados correctamente en {filename}")
    except IOError as e:
        logging.error(f"Error al escribir en el archivo {filename}: {e}")


def main():
    logging.info("Iniciando el proceso de scraping...")

    # Obtener URLs desde el sitemap
    urls = fetch_sitemap(SITEMAP_URL)

    if not urls:
        logging.error("No se encontraron URLs. Saliendo.")
        return

    logging.info(f"Se encontraron {len(urls)} recetas. Extrayendo datos...")

    # Usar hilos para acelerar el scraping
    recipes = []
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_url = {executor.submit(scrape_recipe_data, url): url for url in urls}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                recipe_data = future.result()
                if recipe_data:
                    recipes.append(recipe_data)
            except Exception as e:
                logging.error(f"Error procesando {url}: {e}")

    # Guardar datos en JSON
    save_data_to_json(recipes, JSON_OUTPUT_FILE)
    logging.info("Proceso de scraping completado exitosamente.")


if __name__ == "__main__":
    main()
