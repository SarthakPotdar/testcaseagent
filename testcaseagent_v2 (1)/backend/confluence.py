"""
confluence.py - Fetch and verify Confluence content.
"""

import re
import logging
import requests
from openai import OpenAI
from prompts import CONFLUENCE_SUMMARIZE_PROMPT

logger = logging.getLogger(__name__)


def verify_confluence_access(base_url: str, api_key: str, user_id: str) -> dict:
    base_url = base_url.rstrip("/")
    endpoint = f"{base_url}/rest/api/user/current"
    try:
        resp = requests.get(endpoint, auth=(user_id, api_key),
                            headers={"Accept": "application/json"}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return {"success": True, "user_display_name": data.get("displayName", user_id), "error": None}
        elif resp.status_code == 401:
            return {"success": False, "user_display_name": "", "error": "Invalid credentials. Check your email/API key."}
        elif resp.status_code == 403:
            return {"success": False, "user_display_name": "", "error": "Access forbidden. User may not have Confluence access."}
        else:
            return {"success": False, "user_display_name": "", "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "user_display_name": "", "error": f"Cannot connect to {base_url}. Check the URL."}
    except Exception as e:
        return {"success": False, "user_display_name": "", "error": str(e)}


def fetch_confluence_page(base_url: str, api_key: str, user_id: str, page_id: str) -> dict:
    base_url = base_url.rstrip("/")
    endpoint = f"{base_url}/rest/api/content/{page_id}?expand=body.storage,title"
    try:
        resp = requests.get(endpoint, auth=(user_id, api_key),
                            headers={"Accept": "application/json"}, timeout=15)
        if resp.status_code == 404:
            return {"success": False, "content": "", "title": "", "error": f"Page ID '{page_id}' not found."}
        if resp.status_code == 403:
            return {"success": False, "content": "", "title": "", "error": f"No access to page ID '{page_id}'."}
        resp.raise_for_status()
        data = resp.json()
        html_content = data.get("body", {}).get("storage", {}).get("value", "")
        return {"success": True, "title": data.get("title", "Untitled"),
                "content": _strip_html(html_content), "error": None}
    except Exception as e:
        return {"success": False, "content": "", "title": "", "error": str(e)}


def fetch_confluence_space(base_url: str, api_key: str, user_id: str, space_key: str, max_pages: int = 5) -> list[dict]:
    base_url = base_url.rstrip("/")
    endpoint = f"{base_url}/rest/api/content?spaceKey={space_key}&expand=body.storage,title&limit={max_pages}&type=page"
    try:
        resp = requests.get(endpoint, auth=(user_id, api_key),
                            headers={"Accept": "application/json"}, timeout=15)
        resp.raise_for_status()
        pages = []
        for r in resp.json().get("results", []):
            html = r.get("body", {}).get("storage", {}).get("value", "")
            pages.append({"success": True, "title": r.get("title", ""), "content": _strip_html(html), "error": None})
        return pages
    except Exception as e:
        logger.error(f"Space fetch error: {e}")
        return []


def _strip_html(html: str) -> str:
    html = re.sub(r"<(style|script)[^>]*>.*?</(style|script)>", " ", html, flags=re.DOTALL)
    html = re.sub(r"<[^>]+>", " ", html)
    html = html.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
    lines = [l.strip() for l in html.splitlines() if l.strip()]
    return "\n".join(lines)


def summarize_confluence_content(openai_key: str, content: str) -> str:
    client = OpenAI(api_key=openai_key)
    prompt = CONFLUENCE_SUMMARIZE_PROMPT.format(content=content[:8000])
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1, max_tokens=1500,
    )
    return resp.choices[0].message.content
