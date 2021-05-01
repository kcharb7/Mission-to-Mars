# Mission to Mars
## Overview
### *Purpose*
A Junior Data Scientist, Robin, does freelance astronomy work in her spare time and hopes to one day work at NASA. She had an idea to create a script that captures data on the mission to Mars and hopes to present her findings in a web application to other astrophiles and potentially NASA. Robin would like to gather the most recently published article’s title and summary from the NASA news website.

## Scrape Mars Data: The News
To begin, I imported Splinter and BeautifulSoup in a new Jupyter Notebook file “Mission_to_Mars”:
```
# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
```
Then, I set my executable path:
```
# Set executable path
executable_path = {'executable_path': ChromeDriverManager().install()}
browser = Browser('chrome', **executable_path, headless=False)
```
In a new cell, I assigned the url and instructed the browser to visit it:
```
# Visit the mars nasa news site
url = 'https://redplanetscience.com'
browser.visit(url)
# Optional delay for loading the page
browser.is_element_present_by_css('div.list_text', wait_time=1)
```
Following this, I set up the HTML parser:
```
# Set up the HTML parser
html = browser.html
news_soup = soup(html, 'html.parser')
slide_elem = news_soup.select_one('div.list_text')
```
Next, I chained the .find onto the slide_elem variable to find the content title for the most recent article:
```
# Use the parent element to find the first `a` tag and save it as `news_title`
news_title = slide_elem.find('div', class_='content_title').get_text()
news_title
```
Changing the class in the above code to “article_teaser_body”, I scraped the article summary:
```
# Use the parent element to find the paragraph text
news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
news_p
```

## Scrape Mars Data: Featured Image
The next step was to scrape the featured image from the Jet Propulsion Laboratory’s Space Images webpage. In a new notebook cell, I set up the URL:
```
# Visit URL
url = 'https://spaceimages-mars.com'
browser.visit(url)
```
Then, I added the following code to a new cell to click the full-size image:
```
# Find and click the full image button
full_image_elem = browser.find_by_tag('button')[1]
full_image_elem.click()
```
To scrape the full-size image URL, I added code to parse the data:
```
# Parse the resulting html with soup
html = browser.html
img_soup = soup(html, 'html.parser')
```
I used the img tab and class (<img /> and fancybox-image) to build the URL to the full-size image:
```
# Find the relative image url
img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
img_url_rel
```
Next, I used the base URL to create an absolute URL for accessing the image:
```
# Use the base URL to create an absolute URL
img_url = f'https://spaceimages-mars.com/{img_url_rel}'
img_url
```

## Scrape Mars Data: Mars Facts
Robin additionally wished to have a collection of Mars facts included in her app from the website Galaxy Facts. Robin wished to scrape the table from the Mars Facts page. So, I added “import pandas as pd” to my dependencies and reran the cell. Then, I used Pandas’ read_html() function to scrape the entire table and place that table into a new DataFrame:
```
# Scrape the Mars Facts table and place in DataFrame
df = pd.read_html('https://galaxyfacts-mars.com')[0]
df.columns=['description', 'Mars', 'Earth']
df.set_index('description', inplace=True)
df
```
To convert the DataFrame back into HTML-ready code, I used the to_html() function:
```
# Convert DataFrame back into HTML-ready code
df.to_html()
```
After gathering all the data on Robin’s list, I ended the automated browsing session:
```
# End browsing session
browser.quit()
```

## Export to Python
To make the above code an automated process, I downloaded the code into a Python file. Once downloaded, I cleaned up the code and renamed the file “scraping.py”.

## Use Flask to Create a Web App
Within my Mission-to-Mars directory, I created a new file named “app.py”. Within the file, I imported my tools:
```
# Import tools
from flask import Flask, render_template, redirect, url_for
from flask_pymongo import PyMongo
import scraping
```
Then, I added the following code to set up Flask:
```
# Set up Flask
app = Flask(__name__)
```
Next, I added code to tell Python how to connect to Mongo using PyMongo:
```
# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)
```
I created two Flask routes: one for the main HTML page and the other to scrape new data using the code I created above. I defined the route for the HTML page using the following code:
```
# Define the route for the HTML page
@app.route("/")
def index():
   mars = mongo.db.mars.find_one()
   return render_template("index.html", mars=mars)
```
To create the scraping route, I used the following code:
```
# Define the route for scraping
@app.route("/scrape")
def scrape():
   mars = mongo.db.mars
   mars_data = scraping.scrape_all()
   mars.update({}, mars_data, upsert=True)
   return redirect('/', code=302)
```

## Update the Code
After creating the Flask routes, I updated my code to include functions and error handling. To start, I placed the code for scraping the news title and paragraph summary into a new function called mars_news and included the news_title and news_p in the return statement. I additionally added the word “browser” to the function. Finally, I added a try and except clause right before the scraping to address AttributeErrors:
```
# ## The News
def mars_news(browser):
    # Visit the Mars NASA news site
    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')
    
    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None
```
The code to scrape the featured image was updated in a similar fashion:
```
# ## Featured Images
def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url
```
To update the code for the facts table, I defined a new function called mars_facts and added BaseException to a try and except block:
```
# ## Mars Facts
def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()
```

## Integrate MongoDB Into the Web App
At the top of my scraping.py script, following importing of the dependencies, I added a function called scrape_all to initialize the browser, create a data dictionary, and end the WebDriver and return the scraped data. Within this new function, I added my line of code that initialized the browser:
```
def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)
```
Next, I set my news_title and news_p variables equal to the mars_news(browser) function:
```
    news_title, news_p = mars_news(browser)
```
Subsequently, I created a dictionary that runs all of the functions and stores all of the results. I additionally added the date the code was run last using the dt.datetime.now() function. To use this function, I imported the datetime module. The code to create the dictionary looked as follows:
```
    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_p,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now()
    }
```
To finish the scrape_all function, I added the line browser.quit() and a return statement that returns the data dictionary:
```
    # Stop webdriver and return data
    browser.quit()
    return data
```
At the bottom of my scraping.py script, I added the following:
```
if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())
```

## Create HTML Template
In a new “templates” folder, I created an index.html file and used the exclamation point shortcut to create a basic HTML template. In my index.html file, I added a link for Boostrap’s stylesheet and adjusted the title to “Mission to Mars”
```
<!DOCTYPE html>
<html lang="en">
<head>
   <meta charset="UTF-8" />
   <meta name="viewport" content="width=device-width, initial-scale=1.0" />
   <meta http-equiv="X-UA-Compatible" content="ie=edge" />
   <title>Mission to Mars</title>
   <link
     rel="stylesheet"
     href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"
   />
</head>
<body>
</body>
</html>
```
In the body of my document, I added a <div /> with a class of “container” to set up the container for the Bootstrap components:
```
<body>
  <div class="container">
  </div>
</body>
```
For the header, I created an inner <div /> element with the class “jumbotron text-center” added to the opening tag:
```
  <div class="container">
    <div class="jumbotron text-center">
    </div>
 </div>
```
Within the Jumbotron div, I added the main text and the button to scrape the data:
```
  <div class="container">
    <div class="jumbotron text-center">
       <h1>Mission to Mars</h1>
       <p><a class="btn btn-primary btn-lg" href="/scrape"
                   role="button">Scrape New Data</a></p>
    </div>
 </div>
```
To add in the news article and summary, I first set up the grid underneath the header by creating a new <div /> with a class of “row” and an id of “mars-news”:
```
    <!-- Mars News -->
    <div class="row" id="mars-news">
    </div>
```
Then I added a tag that specified the use of 12 columns so that the article and summary would span the width of the page:
```
    <!-- Mars News -->
    <div class="row" id="mars-news">
      <div class="col-md-12">
  
      </div>
  </div>
```
Next, I nested in two more tags, one with a class of “media” and the other with a class of “media-body” to display the news source as media:
```
    <!-- Mars News -->
    <div class="row" id="mars-news">
      <div class="col-md-12">
       <div class="media">
           <div class="media-body">
   
           </div>
       </div>
      </div>
   </div>
```
I nested a <h2 /> tag inside the media-body <div /> to create a second-level header for the news:
```
           <div class="media-body">
            <h2>Latest Mars News</h2>
   
           </div>
```
Under this tag, I created a fourth-level header for the title of the article:
```
           <div class="media-body">
            <h2>Latest Mars News</h2>
            <h4 class="media-heading">{{mars.news_title}}</h4>
   
           </div>
```
I similarly added the article summary using paragraph tags:
```
<p>{{mars.news_paragraph}}</p>
```
Next, I added code to insert the image underneath the news article by creating a new <div /> with a class of “row” and an id of “mars-featured-image”:
```
    <!-- Featured Image -->
    <div class="row" id="mars-featured-image">

    </div>
```
Next, I added the <div /> for the rows, using 8 columns instead of 12 so that the Mars facts table could go alongside the image:
```
    <!-- Featured Image -->
    <div class="row" id="mars-featured-image">
      <div class="col-md-8">
   
      </div>
   </div>
```
I used an <h2 /> element to add the title “Featured Mars Image” and the <img /> tag with the link to the image to insert the image:
```
        <h2>Featured Mars Image</h2>
        <img
          src="{{mars.featured_image }}"
          class="img-responsive"
          alt="Responsive image"
        />
```
To add the Mars facts table alongside the featured image, I added new code with a column class with four columns after the closing tags of the second <div />:
```
    <!-- Mars Featured Image -->
    <div class="row" id="mars-featured-image">
      <div class="col-md-8">
        <h2>Featured Mars Image</h2>
        <img
          src="{{mars.featured_image }}"
          class="img-responsive"
          alt="Responsive image"
        />
      </div>
      <!-- Mars Facts -->
      <div class="col-md-4">
      </div>
    </div>
```
Within these new tags, I started a new row with a unique id “mars-facts”. Then, I nested the header and table within the row:
```
      <!-- Mars Facts -->
      <div class="col-md-4">
        <div class="row" id="mars-facts">
          <h4>Mars Facts</h4>
          {{ mars.facts | safe }}
        </div>
      </div>
```
Running the Flask app and pressing the “Scrape New Data” button, the final webpage looked as follows:

![Mars_webpage.png](https://github.com/kcharb7/Mission-to-Mars/blob/main/Resources/Mars_webpage.png)


# Challenge
## Overview
### *Purpose*
After reviewing the webpage, Robin wanted to additionally add all four images of Mars’ hemispheres online.

## Scrape Full-Resolution Mars Hemisphere Images and Titles
To begin, I visited the Mars Hemispheres website and used the DevTools to inspect the page for the proper elements to scrape:
```
# Use browser to visit the URL 
url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

browser.visit(url)
```
Once I had identified the HTML tag that holds the links to the full-resolution images, I created a list to hold the .jpg image URL string and title for each hemisphere image. I also created an empty dictionary with the keys “title” and “img_url”. I used Beautiful Soup to parse the HTML and find all “h3” tags and create a list of the titles. Then, I created a for loop that iterated through the list of titles and retrieved the title, clicked on each hemisphere link, navigated to the full-resolution image page, and retrieved the full-resolution image URL string. Within the for loop, the full-resolution image URL string was saved as the value for the “img_url” key and the hemisphere image title was saved as the value for the “title” key in the hem_dict dictionary created. Before moving on to the next URL and title, the dictionary with the added values was appended to the hemisphere_image_urls list. To go back to the main page, I included “browser.visit(url)” in the for loop:
```
# Create a list and dictionary to hold the images and titles.
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
    
    img_url = browser.find_link_by_partial_href('_enhanced.tif/full.jpg')['href']
    
    hem_dict = {'title': title, 'img_url': img_url}
    hemisphere_image_urls.append(hem_dict)
    
    browser.visit(url)
```

Next, I printed the list of dictionary items:
```
# Print the list that holds the dictionary of each image url and title.
hemisphere_image_urls
```

![hemisphere_image_urls.png](https://github.com/kcharb7/Mission-to-Mars/blob/main/Resources/hemisphere_image_urls.png)

After confirming that the image URLs and titles were retrieved for all four hemisphere images, I quit the browser by executing the following code:
```
# Quit the browser
browser.quit()
```

## Update the Web App with Mars’s Hemisphere Images and Titles
After completing the above, I exported the “Mission_to_Mars_Challenge.ipynb” file as a Python file, cleaned up the code, and saved it as “Mission_to_Mars_Challenge.py”. In the def scrape_all() function of my “scraping.py” file, I created a new dictionary in the “data” dictionary to hold a list of dictionaries with the URL string and title of each hemisphere image:
```
    data = {
        "news_title": news_title,
        "news_paragraph": news_p,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemispheres(browser),
        "last_modified": dt.datetime.now()
    }
```
Below the “def mars_facts()” function in the “scraping.py” file, I created a function to scrape the hemisphere data by using my code from the “Mission_to_Mars_Challenge.py”file: 
```
# ## Hemispheres
def hemispheres(browser):
    # Use browser to visit the URL 
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    browser.visit(url)

    # Create a list and dictionary to hold the images and titles.
    hemisphere_image_urls = []

    hem_dict = {}

    # Parse the resulting html with soup
    html = browser.html
    hem_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find all titles
        titles = hem_soup.find_all('h3')

        for i in titles:
            t = i.get_text()
            title = t.strip()
            browser.click_link_by_partial_text(t)
            
            img_url = browser.find_link_by_partial_href('_enhanced.tif/full.jpg')['href']
            
            hem_dict = {'title': title, 'img_url': img_url}
            hemisphere_image_urls.append(hem_dict)
            
            browser.visit(url)
    
    except AttributeError:
        return None

    # Print the list that holds the dictionary of each image url and title.
    return hemisphere_image_urls
```
Next, I modified my “index.html” file to access the Mongo database and look through the dictionary to retrieve the “img_url” and “title”:
```
    <!-- Mars Hemispheres -->
    <div class="row" id="mars-hemispheres">
      <div class="page-header">
        <h2 class="text-center">Mars Hemispheres</h2>
      </div>

      {% for hemisphere in mars.hemispheres %}
      <div class="col-md-6">
        <div class="thumbnail">
          <img src="{{hemisphere.img_url | default('static/images/error.png', true)}}" alt="...">
          <div class="caption">
            <h3>{{hemisphere.title}}</h3>
          </div>
        </div>
      </div>
      {% endfor %}
    </div>
```

## Add Bootstrap 3 Components
Using the Boostrap 3 grid system, I updated my “index.html” file to include .col-xs alongside the .col-md to format the columns to be mobile-responsive. I additionally customized the “Scrape New Data” button to green by changing the button class to “btn btn-success btn-lg”. Finally, I created a linear gradient background colour by adding the following to the body tag:
```
style = "background-image: linear-gradient(#eee, #222);"
```
