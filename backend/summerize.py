import requests
from bs4 import BeautifulSoup
import ollama


OLLAMA_API = "http://localhost:11434/api/chat"
HEADERS = {"Content-Type":"application/json"}
MODEL = "deepseek-r1:8b"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

class Website:

    def __init__(self, url):
        self.url = url
        response = requests.get(url, headers=DEFAULT_HEADERS)
        soup = BeautifulSoup(response.content, 'html.parser') 
        self.title = soup.title.string if soup.title else "No title found"

        for irrelevant in soup.body(["script", "style", "img", "input"]): 
            irrelevant.decompose()
        self.text = soup.body.get_text(separator="\n", strip=True)
        
system_prompt = (
    "You are a web-content analysis assistant. "
    "You will receive a Website object with two attributes: "
    "`title` and `text`. Ignore any navigation-related text "
    "and produce a concise summary in Markdown, starting with the page title as a heading."
)

def user_prompt_for(website):
    return (
        f"You are looking at a website titled “{website.title}”. "
        "Please summarize it in detail:\n\n"
        f"{website.text}"
    )

def make_chat(website):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_prompt_for(website)}
    ]
    return ollama.chat(
        model=MODEL,
        messages=messages,
        stream=False
    )
    
site = Website("https://www.onuronel.dev/")
response = make_chat(site)
print(response["message"]["content"])