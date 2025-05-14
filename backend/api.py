from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
import requests
from bs4 import BeautifulSoup
import ollama

MODEL = "deepseek-r1:8b"
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

SYSTEM_PROMPT = (
    "You are a web-content analysis assistant. "
    "You will receive a Website object with two attributes: "
    "`title` and `text`. Ignore any navigation-related text "
    "and produce a concise summary in Markdown, starting with the page title as a heading."
)

class SummarizeRequest(BaseModel):
    url: HttpUrl

class SummarizeResponse(BaseModel):
    title: str
    summary: str

class Website:
    def __init__(self, url: str):
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")
        self.title = soup.title.string if soup.title else "No title found"
        body = soup.body or soup
        for tag in body(["script", "style", "img", "input"]):
            tag.decompose()
        self.text = body.get_text(separator="\n", strip=True)

def user_prompt_for(website: Website) -> str:
    return (
        f"You are looking at a website titled “{website.title}”. "
        "Please summarize it in detail:\n\n"
        f"{website.text}"
    )

def make_chat(website: Website) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": user_prompt_for(website)}
    ]
    result = ollama.chat(model=MODEL, messages=messages, stream=False)
    return result["message"]["content"]

router = APIRouter()

@router.post("/summarize", response_model=SummarizeResponse)
async def summarize(payload: SummarizeRequest):
    try:
        site = Website(payload.url)
        summary_md = make_chat(site)
        return SummarizeResponse(title=site.title, summary=summary_md)
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"URL erişim hatası: {e}")
    except KeyError:
        raise HTTPException(status_code=500, detail="Beklenmeyen yanıt formatı")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sunucu hatası: {e}")
