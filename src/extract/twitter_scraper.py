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

class TwitterScraper:
    def __init__(self, email=None, password=None, username=None, headless=True):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        self.email = email
        self.password = password
        self.username = username
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
        login_url = "https://twitter.com/login"
        try:
            self.driver.get(login_url)

            email_input_xpath = "//input[@name='text' or @name='username']"
            email_field = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, email_input_xpath))
            )
            email_field.send_keys(self.email)

            next_button_xpath = "//button[@role='button']//span[text()='Avançar']"
            next_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, next_button_xpath))
            )
            next_button.click()

            try:
                username_input_xpath = "//input[@name='text']"
                username_field = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, username_input_xpath))
                )
                if username_field:
                    username_field.send_keys(self.username)

                    confirmar_button_xpath = "//button[@role='button']//span[text()='Avançar']"
                    confirmar_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, confirmar_button_xpath))
                    )
                    confirmar_button.click()
            except TimeoutException:
                pass

            password_input_xpath = "//input[@name='password' or @data-testid='ChallengePassword']"
            password_field = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, password_input_xpath))
            )
            password_field.send_keys(self.password)

            login_button_xpath = "//button[@data-testid='LoginForm_Login_Button']//span[text()='Entrar']"
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, login_button_xpath))
            )
            login_button.click()

            logged_in_indicator_xpath = "//a[@data-testid='AppTabBar_Home_Link'] | //div[@data-testid='tweetComposer']"
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, logged_in_indicator_xpath))
            )
            return True

        except TimeoutException as e:
            raise Exception(f"Tempo limite excedido durante o login: {e}")
        except NoSuchElementException as e:
            raise Exception(f"Elemento não encontrado durante o login: {e}. A estrutura da página do Twitter (X) pode ter mudado.")
        except WebDriverException as e:
            raise Exception(f"Erro do WebDriver durante o login: {e}. Verifique se o driver do navegador está configurado corretamente e é compatível com seu navegador.")
        except Exception as e:
            raise Exception(f"Ocorreu um erro inesperado durante o login: {e}")

    def get_page_content(self, url):
        try:
            self.driver.get(url)
            time.sleep(random.uniform(4, 7))

            for _ in range(2):
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

        tweet_containers = soup.find_all('article', {'role': 'article'})

        for tweet_container in tweet_containers:
            try:
                author_name = "N/A"
                author_name_element = tweet_container.find('div', {'data-testid': 'User-Name'})
                if author_name_element:
                    span = author_name_element.find('span')
                    if span and span.get_text(strip=True):
                        author_name = span.get_text(strip=True)

                full_post_content = "N/A"
                full_post_content_element = tweet_container.find('div', {'data-testid': 'tweetText'})
                if full_post_content_element:
                    full_post_content = full_post_content_element.get_text(strip=True, separator='\n')
                
                if not full_post_content or full_post_content.strip() == "" or full_post_content == "N/A":
                    continue

                interactions = {
                    'replies': '0',
                    'reposts': '0',
                    'likes': '0',
                    'views': '0'
                }

                interactions_bar = tweet_container.find('div', {'role': 'group'})
                if interactions_bar:
                    reply_button = interactions_bar.find('button', {'data-testid': 'reply'})
                    if reply_button:
                        replies_span = reply_button.find('span', class_='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3')
                        if replies_span:
                            interactions['replies'] = replies_span.get_text(strip=True)

                    repost_button = interactions_bar.find('button', {'data-testid': 'retweet'})
                    if repost_button:
                        reposts_span = repost_button.find('span', class_='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3')
                        if reposts_span:
                            interactions['reposts'] = reposts_span.get_text(strip=True)

                    like_button = interactions_bar.find('button', {'data-testid': 'like'})
                    if like_button:
                        likes_span = like_button.find('span', class_='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3')
                        if likes_span:
                            interactions['likes'] = likes_span.get_text(strip=True)

                    views_link = interactions_bar.find('a', {'aria-label': lambda value: value and 'views' in value})
                    if views_link:
                        views_span = views_link.find('span', class_='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3')
                        if views_span:
                            interactions['views'] = views_span.get_text(strip=True)

                posts_data.append({
                    'author_name': author_name,
                    'full_post_content': full_post_content,
                    'interactions': interactions
                })

            except Exception as e:
                print(f"⚠️ Erro ao parsear um post: {e}. HTML parcial:\n{tweet_container.prettify()[:500]}...")
        
        return posts_data


    def get_relevant_posts(self, search_query=None, recent=False):
        encoded_query = urllib.parse.quote_plus(search_query)
        if recent:
            target_url = f"https://x.com/search?q={encoded_query}&f=live"
        else:
            target_url = f"https://x.com/search?q={encoded_query}&src=trend_click&vertical=trends"

        html_content = self.get_page_content(target_url)

        if html_content:
            posts = self._parse_posts(html_content)
            return posts
        else:
            raise Exception("Não foi possível recuperar o conteúdo da página.")

    def close_driver(self):
        if self.driver:
            self.driver.quit()