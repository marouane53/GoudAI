import requests
import ast
from newspaper import Article
import re
import time

ANTHROPIC_API_KEY = "YOUR API KEY"  # Replace with your Anthropic API key
SERP_API_KEY = "YOUR API KEY"  # Replace with your SERP API key

def get_search_terms(topic):
    system_prompt = "You are a world-class journalist. Generate a list of 5 search terms to search for to research and write an article about the topic."
    messages = [
        {"role": "user", "content": f"Please provide a list of 5 search terms related to '{topic}' for researching and writing an article. Respond with the search terms in a comma-separated list, without any other text."},
    ]
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    data = {
        "model": 'claude-3-haiku-20240307',
        "max_tokens": 200,
        "temperature": 0.5,
        "system": system_prompt,
        "messages": messages,
    }

    response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data)
    response_text = response.json()['content'][0]['text']
    search_terms = [term.strip() for term in response_text.split(',')]
    return search_terms

def get_search_results(search_term):
    url = f"https://serpapi.com/search.json?q={search_term}&api_key={SERP_API_KEY}"
    response = requests.get(url)
    data = response.json()
    return data.get('organic_results', [])

def select_relevant_urls(search_results):
    system_prompt = "You are a journalist assistant. From the given search results, select the URLs that seem most relevant and informative for writing an article on the topic."
    search_results_text = "\n".join([f"{i+1}. {result['link']}" for i, result in enumerate(search_results)])
    messages = [
        {"role": "user", "content": f"Search Results:\n{search_results_text}\n\nPlease select the numbers of the URLs that seem most relevant and informative for writing an article on the topic. Respond with the numbers separated by commas, without any other text."},
    ]
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    data = {
        "model": 'claude-3-haiku-20240307',
        "max_tokens": 200,
        "temperature": 0.5,
        "system": system_prompt,
        "messages": messages,
    }
    response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data)
    response_text = response.json()['content'][0]['text']

    numbers = re.findall(r'\d+', response_text)
    relevant_indices = [int(num) - 1 for num in numbers]
    relevant_urls = [search_results[i]['link'] for i in relevant_indices if i < len(search_results)]

    return relevant_urls

def get_article_text(url):
    article = Article(url)
    article.download()
    article.parse()
    return article.text

def write_article(topic, article_texts):
    system_prompt = "You are a Moroccan journalist who only writes in Moroccan Arabic Darija. Write a high-quality, NYT-worthy article on the given topic based on the provided article texts. The article should be well-structured, informative, and engaging."
    combined_text = "\n\n".join(article_texts)
    messages = [
        {"role": "user", "content": f"Topic: {topic}\n\nArticle Texts:\n{combined_text}\n\nPlease write a high-quality, NYT-worthy article on the topic based on the provided article texts in Moroccan Arabic Darija. The article should be well-structured, informative, and engaging. Ensure the length is at least as long as a NYT cover story -- at a minimum, 15 paragraphs. Also, please provide a title in English for the article in the format 'Title: [article title]' at the beginning of your response, only the title in english but the rest is in Moroccan Arabic Darija."},
    ]
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    data = {
        "model": 'claude-3-opus-20240229',
        "max_tokens": 3000,
        "temperature": 0.5,
        "system": system_prompt,
        "messages": messages,
    }
    try:
        response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data)
        response_json = response.json()
        if 'content' in response_json:
            response_text = response_json['content'][0]['text']
            title, article = response_text.split('\n', 1)
            title = title.replace("Title: ", "").strip()
            return title, article.strip()
        else:
            print("Error: 'content' key not found in the API response.")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while making the API request: {e}")
        return None, None


def edit_article(article, max_retries=3, retry_delay=5):
    system_prompt = "who is knowledgeable in Moroccan Arabic Darija. Review the given article and provide suggestions for improvement. Focus on clarity, coherence, and overall quality."
    messages = [
        {"role": "user", "content": f"Article:\n{article}\n\nPlease review the article and provide suggestions for improvement. Focus on clarity, coherence, and overall quality."},
    ]
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    data = {
        "model": 'claude-3-opus-20240229',
        "max_tokens": 3000,
        "temperature": 0.5,
        "system": system_prompt,
        "messages": messages,
    }

    retry_count = 0
    while retry_count < max_retries:
        try:
            response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data)
            response_json = response.json()

            if 'content' in response_json:
                suggestions = response_json['content'][0]['text']
                break
            else:
                print("Error: 'content' key not found in the API response for suggestions. Retrying...")
                retry_count += 1
                time.sleep(retry_delay)
        except requests.exceptions.RequestException as e:
            print(f"Error occurred while making the API request for suggestions: {e}. Retrying...")
            retry_count += 1
            time.sleep(retry_delay)

    if retry_count == max_retries:
        print("Error: Failed to retrieve suggestions after multiple retries.")
        return None

    system_prompt = "You are an editor who is knowledgeable in Moroccan Arabic Darija. Rewrite the given article based on the provided suggestions for improvement, and rewrite it in the Moroccan Arabic Darija please."
    messages = [
        {"role": "user", "content": f"Original Article:\n{article}\n\nSuggestions for Improvement:\n{suggestions}\n\nPlease rewrite the article based on the provided suggestions for improvement."},
    ]
    data = {
        "model": 'claude-3-opus-20240229',
        "max_tokens": 3000,
        "temperature": 0.5,
        "system": system_prompt,
        "messages": messages,
    }

    retry_count = 0
    while retry_count < max_retries:
        try:
            response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data)
            response_json = response.json()

            if 'content' in response_json:
                edited_article = response_json['content'][0]['text']
                return edited_article
            else:
                print("Error: 'content' key not found in the API response for edited article. Retrying...")
                retry_count += 1
                time.sleep(retry_delay)
        except requests.exceptions.RequestException as e:
            print(f"Error occurred while making the API request for edited article: {e}. Retrying...")
            retry_count += 1
            time.sleep(retry_delay)

    print("Error: Failed to generate the edited article after multiple retries.")
    return None



def format_filename(title):
    # Remove any characters that are not alphanumeric, space, or underscore
    formatted_title = re.sub(r'[^a-zA-Z0-9 _]', '', title)
    # Replace spaces with underscores
    formatted_title = formatted_title.replace(' ', '_')
    return formatted_title

# User input
topic = input("Enter a topic to write about: ")
do_edit = input("After the initial draft, do you want an automatic edit? This may improve performance, but is slightly unreliable. Answer 'yes' or 'no': ")

# Generate search terms
search_terms = get_search_terms(topic)
print(f"\nSearch Terms for '{topic}':")
print(", ".join(search_terms))

# Perform searches and select relevant URLs
relevant_urls = []
for term in search_terms:
    search_results = get_search_results(term)
    urls = select_relevant_urls(search_results)
    relevant_urls.extend(urls)

print('Relevant URLs to read:', relevant_urls)

# Get article text from relevant URLs
article_texts = []
for url in relevant_urls:
    try:
        text = get_article_text(url)
        if len(text) > 75:
            article_texts.append(text)
    except:
        pass

print('Articles to reference:', article_texts)

print('\n\nWriting article...')
# Write the article
title, article = write_article(topic, article_texts)

if title and article:
    print("\nGenerated Article:")
    print(article)

    # Format the title for the file name
    formatted_title = format_filename(title)

    # Save the article to a text file with UTF-8 encoding
    with open(f"{formatted_title}.txt", "w", encoding='utf-8') as file:
        file.write(article)
    print(f"\nArticle saved to {formatted_title}.txt")

    if 'y' in do_edit.lower():
        # Edit the article
        edited_article = edit_article(article)
        if edited_article:
            print("\nEdited Article:")
            print(edited_article)
            
            # Save the edited article to a text file with UTF-8 encoding
            with open(f"{formatted_title}_edited.txt", "w", encoding='utf-8') as file:
                file.write(edited_article)
            print(f"\nEdited article saved to {formatted_title}_edited.txt")
        else:
            print("Error: Failed to generate the edited article.")
else:
    print("Error: Failed to generate the article.")
