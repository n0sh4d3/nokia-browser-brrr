import re
import time
from concurrent.futures import ThreadPoolExecutor
import sys
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

nlp = None


def load_nlp():
    global nlp
    if nlp is None:
        import pytextrank
        import spacy

        nlp = spacy.load("en_core_web_lg")
        nlp.add_pipe("textrank")
    return nlp


def search():
    search = input("kurwa szukaj: ")
    results = DDGS().text(search, max_results=10)
    for i, _ in enumerate(results):
        print(f"[{i}]Result: {results[i]['title']}")
    user_choice = int(input("wybierz kurwa zeby link miec: "))
    link = results[user_choice]["href"]
    return link


def fetch_content(link):
    try:
        page = requests.get(link, timeout=10)
        return page.text
    except requests.exceptions.RequestException:
        sys.exit(1)


def parse_content(html):
    soup = BeautifulSoup(html, "html.parser")

    p_elems = [
        p.get_text(strip=True)
        for p in soup.find_all("p")
        if len(p.get_text(strip=True)) > 40
    ]
    return " ".join(p_elems)


def is_recipe(text):
    recipe_keywords = [
        "ingredients",
        "preparation",
        "instructions",
        "cup",
        "tablespoon",
        "teaspoon",
    ]
    return (
        any(keyword in text.lower() for keyword in recipe_keywords)
        and sum(1 for _ in re.finditer(r"\b\d+\s+(cup|tbsp|tsp|oz|g)\b", text.lower()))
        > 3
    )


def is_lyrics(text):
    return (
        "[verse]" in text.lower()
        or "[chorus]" in text.lower()
        or len(re.findall(r"\n\s*\n", text)) > text.count(".") * 0.7
    )


def detect_content_type(text):
    if is_recipe(text):
        return "recipe"
    if is_lyrics(text):
        return "lyrics"
    return "article"


def summarize_text(text, max_sentences=20):
    nlp = load_nlp()

    if len(text) > 100000:
        text = text[:100000]

    doc = nlp(text)

    sentences = list(doc.sents)
    total_sentences = len(sentences)

    if total_sentences > 100:
        summary_percentage = 0.15
    elif total_sentences > 50:
        summary_percentage = 0.25
    else:
        summary_percentage = 0.4

    summary_sentence_count = max(
        3, min(max_sentences, int(total_sentences * summary_percentage))
    )

    summary_sentences = [
        str(sent)
        for sent in doc._.textrank.summary(limit_sentences=summary_sentence_count)
    ]
    return summary_sentences, total_sentences


def main():
    start_time = time.time()
    link = search()
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_content = executor.submit(fetch_content, link)
        future_nlp = executor.submit(load_nlp)
        html_content = future_content.result()
        cleaned_text = parse_content(html_content)
        content_type = detect_content_type(cleaned_text)
        future_nlp.result()

    if content_type in ["recipe", "lyrics"]:
        print(
            f"Detected {content_type} content. Displaying original text without summarization:"
        )

        print(cleaned_text[:1000] + "..." if len(cleaned_text) > 1000 else cleaned_text)
    else:
        summary_sentences, total_sentences = summarize_text(cleaned_text)
        full_summary = " ".join(summary_sentences)

        print(f"orginalny yap ma: {total_sentences} zdan")
        print(f"podsumowanie ma: {len(summary_sentences)} zdan")
        print("\npodsumowanko:")
        print(full_summary)

    print(f"\nzajelo to kurwa cale: {time.time() - start_time:.2f} sekundek")


if __name__ == "__main__":
    main()

