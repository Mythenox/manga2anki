from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin
import requests

#TODO: Coroutines
"""TODO: instead of fetching the first result, make sure the text (maybe normalized form?) appears in the result,
and that the part of speech matches (solves the problem of どう (adverb) being matched to 銅 (copper))
"""   

def main():
    pass

def get_html(url: str) -> str | None:
    resp = requests.get(url, headers={"User-Agent": "JishoQuery"})
    content_header: str | None = resp.headers.get('content-type')
    if resp.status_code >= 400:
        resp.raise_for_status()
    elif content_header is None or 'text/html' not in content_header:
        raise Exception("invalid content type")
    page_html = resp.text
    soup = BeautifulSoup(page_html, 'html.parser')
    result = soup.find("div", id="result_area")
    if isinstance(result, Tag):
        if result.find("div", id="no-matches"):
            return None
    return page_html

def fetch_word_html(url: str) -> str | None:
    # used in the case in which the direct jisho.org/word/~ link doesn't work
    html = get_html(url)
    if html is not None:
        soup = BeautifulSoup(html, 'html.parser')
        result = soup.find("a", class_="light-details_link")
        if isinstance(result, Tag):
            href = result.get("href")
            if isinstance(href, str):
                word_link = urljoin("https://", href)
                return get_html(word_link)
    return None

def get_tango_jlpt_rating(html: str) -> int | None:
    soup = BeautifulSoup(html, 'html.parser')
    result = soup.find("span", class_="concept_light-tag label")
    if isinstance(result, Tag) and "JLPT" in result.text:
        jlpt_rating = int(result.text[-1])
        return jlpt_rating
    return None


def get_kanji_jlpt_rating(html: str) -> int | None:
    soup = BeautifulSoup(html, 'html.parser')
    parent_div = soup.find("div", class_="jlpt")
    if isinstance(parent_div, Tag):
        result = parent_div.strong
        if isinstance(result, Tag):
            jlpt_rating = int(result.text[-1])
            return jlpt_rating
        return None
    return None


def get_tango_english_meaning(html: str) -> str | None:
    # some words have a million different definitions on jisho.org, so I'm gonna compromise and just grab the first one
    soup = BeautifulSoup(html, 'html.parser')
    result = soup.find("span", class_="meaning-meaning")
    if isinstance(result, Tag):
        meaning = result.text.strip()
        return meaning
    return None
    
    
def get_kanji_english_meaning(html: str) -> str | None:
    soup = BeautifulSoup(html, 'html.parser')
    result = soup.find("div", class_="kanji-details__main-meanings")
    if isinstance(result, Tag):
        meaning = result.text.strip()
        return meaning
    return None

def get_kanji_readings(html: str) -> dict[str, list[str]] | None:
    """return dictionary (keys: kunyomi, onyomi) of lists of possible readings"""
    soup = BeautifulSoup(html, 'html.parser')
    kunyomi_result = soup.find("dl", class_="dictionary_entry kun_yomi")
    onyomi_result = soup.find_all("dl", class_="dictionary_entry on_yomi")[2]

    if kunyomi_result is None and onyomi_result is None:
        return None
    
    if isinstance(kunyomi_result, Tag):
        dd_kun = kunyomi_result.find("dd", class_="kanji-details__main-readings-list")
        if dd_kun:
            kunyomi_list = [elt.text for elt in dd_kun.find_all("a")]
        else:
            kunyomi_list = []
    else:
        kunyomi_list = []

    if isinstance(onyomi_result, Tag):
        dd_on = onyomi_result.find("dd", class_="kanji-details__main-readings-list")# class_="kanji-details__main-readings-list"
        if dd_on is not None:
            onyomi_list = [elt.text for elt in dd_on.find_all("a")]  
        else:
            onyomi_list = []
    else:
        onyomi_list = []

    readings: dict[str, list[str]] = {"kunyomi": kunyomi_list, "onyomi": onyomi_list}
    return readings


if __name__ == "__main__":
    main()