import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from urllib.parse import urljoin

class SiteSummarizer:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def scrape_and_summarize(self, url, visited=None):
        if visited is None:
            visited = set()

        # Check if the URL has already been visited
        if url in visited:
            return None
        visited.add(url)

        # Scrape the HTML site
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses
        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract relevant text content
        text = "\n".join(paragraph.get_text() for paragraph in soup.find_all("p")).strip()
        if not text:
            print(f"No text found at {url}")
            return None

        print(f"Extracted text from {url}: {text}")

        # Generate a summary using GPT-4
        prompt = f"Please summarize the following text:\n\n{text}"
        summary = ""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                n=1,
                stop=None,
                temperature=0.7,
                request_timeout=15
            )
            summary = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error during OpenAI API call for {url}: {e}")
            return {"url": url, "summary": None, "internal_summaries": []}

        # Find and follow internal links
        summaries = []
        for link in soup.find_all("a"):
            href = link.get("href")
            if href and not href.startswith("http"):
                # Convert relative URL to absolute URL
                internal_url = urljoin(url, href)
                internal_summary = self.scrape_and_summarize(internal_url, visited)
                if internal_summary:
                    summaries.append(internal_summary)

        return {"url": url, "summary": summary, "internal_summaries": summaries}

# Example usage:
# summarizer = SiteSummarizer(api_key='your_api_key_here')
# result = summarizer.scrape_and_summarize('https://example.com')
# print(result)
