import wikipediaapi
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests


app = Flask(__name__)

wiki_wiki = wikipediaapi.Wikipedia(
    user_agent='MyWebPortfolio (anna.rozumova108@gmail.com)',
        language='en',
        extract_format=wikipediaapi.ExtractFormat.HTML
)

@app.route('/query', methods=['POST'])
def query_wikipedia():
    data = request.get_json()
    query = data.get('query', '')

    if not query:
        return jsonify({'error': 'No query provided'}), 400
        
    # Fetch Wikipedia page
    page = wiki_wiki.page(query)
    if not page.exists():
        return jsonify({'error': f"No article found for '{query}'"}), 404

    # Extract article details
    title = page.title
    raw_summary = page.summary[:500] + "..." if len(page.summary) > 500 else page.summary
    url = page.fullurl

    soup = BeautifulSoup(raw_summary, 'html.parser')
    summary = soup.get_text()

    main_image = None
    response = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}")
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