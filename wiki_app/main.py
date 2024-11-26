import wikipediaapi
from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

wiki_wiki = wikipediaapi.Wikipedia(
    user_agent='MyProjectName (merlin@example.com)',
        language='en',
        extract_format=wikipediaapi.ExtractFormat.HTML
)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        
        # Fetch Wikipedia page
        page = wiki_wiki.page(query)
        
        if not page.exists():
            return render_template('index.html', error=f"No article found for '{query}'")

        # Extract article details
        title = page.title
        raw_summary = page.summary[:500] + "..." if len(page.summary) > 500 else page.summary
        url = page.fullurl

        soup = BeautifulSoup(raw_summary, 'html.parser')
        summary = soup.get_text()


        # Get the first image from the page
        main_image = None
        response = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}")
        if response.status_code == 200:
            data = response.json()
            main_image = data.get('thumbnail', {}).get('source', None)

        return render_template(
            'index.html',
            title=title,
            summary=summary,
            main_image=main_image,
            url=url
        )
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=8000)