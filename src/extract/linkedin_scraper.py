import requests
from bs4 import BeautifulSoup
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

import urllib.parse

class LinkedInScraper:
    def __init__(self, email=None, password=None, headless=True):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        self.email = email
        self.password = password
        self.headless = headless
        self.driver = self._initialize_driver()
        self.driver.set_window_size(1920, 1080)

    def _initialize_driver(self):
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            driver.set_page_load_timeout(30)
            return driver
        except Exception as e:
            raise Exception(f"Erro ao inicializar o WebDriver: {e}")

    def _login(self):
        login_url = "https://www.linkedin.com/login"
        try:
            self.driver.get(login_url)

            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username_field.send_keys(self.email)

            password_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "password"))
            )
            password_field.send_keys(self.password)

            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )
            login_button.click()

            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "global-nav-typeahead"))
            )
            return True
        except TimeoutException:
            raise Exception("Tempo limite excedido ao tentar fazer login. Credenciais incorretas ou CAPTCHA/bloqueio.")

        except NoSuchElementException:
            raise Exception("Elemento de login não encontrado. A estrutura da página pode ter mudado.")
        except Exception as e:
            raise Exception(f"Erro durante o login: {e}")

    def get_page_content(self, url, roll_count):
        try:
            self.driver.get(url)
            time.sleep(random.uniform(2, 3))

            for _ in range(roll_count):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(2, 5))

            return self.driver.page_source
        except TimeoutException:
            raise Exception(f"Tempo limite excedido ao carregar a página: {url}")
        except Exception as e:
            raise Exception(f"Erro ao buscar a página: {e}")

    def _parse_posts(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        posts_data = []

        post_elements = soup.find_all('li', class_='artdeco-card mb2')

        for post_element in post_elements:
            try:
                author_name = "N/A"
                author_name_element_outer = post_element.find('span', class_='update-components-actor__title')
                if author_name_element_outer:
                    author_name_element_inner = author_name_element_outer.find('span', class_='hoverable-link-text')
                    author_name = author_name_element_inner.get_text(strip=True) if author_name_element_inner else "N/A"

                full_post_content = "N/A"
                main_post_content_span = post_element.find('span', class_=['break-words', 'tvm-parent-container'])
                if main_post_content_span:
                    full_post_content = main_post_content_span.get_text(strip=True, separator='\n')
                
                reactions_count = "N/A"
                reactions_element = post_element.find('span', class_='social-details-social-counts__reactions-count')
                if reactions_element:
                    reactions_count = reactions_element.get_text(strip=True)

                if full_post_content != "N/A" and full_post_content.strip() != "":
                    posts_data.append({
                        'author_name': author_name,
                        'full_post_content': full_post_content,
                        'reactions_count': reactions_count
                    })
            except Exception as e:
                raise Exception(f"Erro ao parsear um post: {e}. HTML do post:\n{post_element}")

        return posts_data

    def get_relevant_posts(self, search_query=None, roll_count=2):
        encoded_query = urllib.parse.quote_plus(search_query)
        target_url = f"https://www.linkedin.com/search/results/content/?keywords={encoded_query}&origin=GLOBAL_SEARCH_HEADER"

        html_content = self.get_page_content(target_url, roll_count=roll_count)

        if html_content:
            posts = self._parse_posts(html_content)
            return posts
        else:
            raise Exception("Não foi possível recuperar o conteúdo da página.")

    def close_driver(self):
        if self.driver:
            self.driver.quit()