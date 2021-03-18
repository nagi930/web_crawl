from urllib.parse import quote
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd


pd.options.display.max_rows = 1000
pd.options.display.max_columns = 1000

search = input('search\n')
_quote = quote(search)
url = f'https://www.youtube.com/results?search_query={_quote}'

options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome('./webdriver/chrome/chromedriver.exe', options=options)

driver.get(url)
driver.implicitly_wait(10)
html = driver.page_source.encode('utf-8')
soup = BeautifulSoup(html, 'html.parser')

df_video = pd.DataFrame(columns=['channel', 'title', 'video_url', 'views', 'date'])
df_playlist = pd.DataFrame(columns=['channel', 'title', 'video_url'])

videos = soup.find_all('div', id='meta')[:-1]

for i, video in enumerate(videos):
    channel = video.find('div', class_="style-scope ytd-channel-name", id="text-container").text.strip()
    title = video.find('yt-formatted-string', class_="style-scope ytd-video-renderer").text
    video_url = f"https://www.youtube.com{video.find('a', class_='yt-simple-endpoint style-scope ytd-video-renderer', id='video-title')['href']}"
    views = video.find('div', class_="style-scope ytd-video-meta-block", id="metadata-line").text.split('\n')[1].strip()
    date = video.find('div', class_="style-scope ytd-video-meta-block", id="metadata-line").text.split('\n')[2].strip()
    df_video.loc[i] = [channel, title, video_url, views, date]


playlists = soup.find_all('div', class_="style-scope ytd-playlist-renderer", id="content")

for i, playlist in enumerate(playlists):
    p_channel = playlist.find('a', class_="yt-simple-endpoint style-scope yt-formatted-string").text
    p_title = playlist.find('span', class_="style-scope ytd-playlist-renderer", id="video-title").text.strip()
    p_video_url = f"https://www.youtube.com{playlist.find('yt-formatted-string', class_='style-scope ytd-playlist-renderer', id='view-more').contents[0]['href']}"
    df_playlist.loc[i] = [p_channel, p_title, p_video_url]


print(df_video)
print(df_playlist)