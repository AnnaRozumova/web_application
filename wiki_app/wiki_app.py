'''This Flask application provides an API endpoint to fetch Wikipedia articles 
based on a user query. It extracts the article's title, summary, full URL, 
and main image (if available).'''
import wikipediaapi
from flask import Flask, request, jsonify, Response, make_response
from bs4 import BeautifulSoup
import requests


app = Flask(__name__)

wiki_wiki = wikipediaapi.Wikipedia(
    user_agent='MyWebPortfolio (anna.rozumova108@gmail.com)',
        language='en',
        extract_format=wikipediaapi.ExtractFormat.HTML
)

@app.route('/query', methods=['POST'])
def query_wikipedia() -> Response:
    '''Fetch Wikipedia page and extract article details'''
    data = request.get_json()
    query = data.get('query', '')

    if not query:
        return jsonify({'error': 'No query provided'})
    page = wiki_wiki.page(query)
    if not page.exists():
        return jsonify({'error': f"No article found for '{query}'"})

    title = page.title
    raw_summary = page.summary[:500] + "..." if len(page.summary) > 500 else page.summary
    url = page.fullurl

    soup = BeautifulSoup(raw_summary, 'html.parser')
    summary = soup.get_text()

    main_image = None
    response = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}", timeout=30)
    if response.status_code == 200:
        data = response.json()
        main_image = data.get('thumbnail', {}).get('source', None)

    return jsonify({
        'title': title,
        'summary': summary,
        'url': url,
        'main_image': main_image,
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=8000)
