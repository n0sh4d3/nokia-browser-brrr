from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import requests


def main():
    search = input("kurwa szukaj: ")
    results = DDGS().text(search, max_results=2)
    # results have 'title' and 'href' keys
    for i, _ in enumerate(results):
        print(f"[{i}]Result: {results[i]['title']}")

    # ^ to musi trafic jako smsesik
    # wartosc z smsika musi bytc wybrana z tego miejsca kurwa
    # jak wszystko git, to scrapuj kurwa strone, pozbac sie htmel tagow i wyslij
    user_chocie = int(input("wybierz kurwa zeby link miec: "))
    link = results[user_chocie]["href"]
    r = requests.get(link)
    resp_body = r.content
    soup = BeautifulSoup(resp_body, "html.parser")
    search_text = soup.get_text()
    cleaneed_up = search_text.replace("\n", "")
    print(cleaneed_up)


if __name__ == "__main__":
    main()
