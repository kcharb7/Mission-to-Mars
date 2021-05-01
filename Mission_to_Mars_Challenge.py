# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

# Set up Splinter
executable_path = {'executable_path': ChromeDriverManager().install()}
browser = Browser('chrome', **executable_path)

# Visit the Mars NASA news site
url = 'https://redplanetscience.com'
browser.visit(url)

# Optional delay for loading the page
browser.is_element_present_by_css('div.list_text', wait_time=1)

# Convert the browser html to a soup object and then quit the browser
html = browser.html
news_soup = soup(html, 'html.parser')
slide_elem = news_soup.select_one('div.list_text')

# Use the parent element to find the first `a` tag and save it as `news_title`
news_title = slide_elem.find('div', class_='content_title').get_text()
news_title

# Use the parent element to find the paragraph text
news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
news_p


# ### Featured Images

# Visit URL
url = 'https://spaceimages-mars.com'
browser.visit(url)

# Find and click the full image button
full_image_elem = browser.find_by_tag('button')[1]
full_image_elem.click()

# Parse the resulting html with soup
html = browser.html
img_soup = soup(html, 'html.parser')

# Find the relative image url
img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
img_url_rel

# Use the base URL to create an absolute URL
img_url = f'https://spaceimages-mars.com/{img_url_rel}'
img_url


# ### Mars Facts

# Scrape the Mars Facts table and place in DataFrame
df = pd.read_html('https://galaxyfacts-mars.com')[0]
df.columns=['description', 'Mars', 'Earth']
df.set_index('description', inplace=True)
df

# Convert DataFrame back into HTML-ready code
df.to_html()


# # Scrape High-Resolution Mars’ Hemisphere Images and Titles

# ### Hemispheres

# Use browser to visit the URL 
url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

browser.visit(url)

# Create a list to hold the images and titles.
hemisphere_image_urls = []

hem_dict = {}

# Parse the resulting html with soup
html = browser.html
hem_soup = soup(html, 'html.parser')

# Write code to retrieve the image urls and titles for each hemisphere. 
# Find all titles
titles = hem_soup.find_all('h3')

for i in titles:
    t = i.get_text()
    title = t.strip()
    browser.click_link_by_partial_text(t)
    
    href = browser.find_link_by_partial_href('_enhanced.tif/full.jpg')['href']
    img_url = f'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars/{href}'
    
    hem_dict = {'title': title, 'img_url': img_url}
    hemisphere_image_urls.append(hem_dict)
    
    browser.visit(url)

# Print the list that holds the dictionary of each image url and title.
hemisphere_image_urls

# Quit the browser
browser.quit()
