import wikipedia
import networkx as nx
import requests
from bs4 import BeautifulSoup


links_dictionary = {}


# Returns a list of links from the 'See Also' section of Wikipedia
def see_also_links(url):
    result = requests.get(url)
    soup = BeautifulSoup(result.content, 'lxml')
    try:
        see_also = soup.find(id='See_also')
        links = []
        see_also = see_also.find_next('ul')
    except AttributeError:
        return []

    again = True
    while again:
        try:
            if 'Portal:' in see_also.find('a')['title']:
                again = True
                see_also = see_also.find_next('ul')
                continue
            for a in see_also.find_all('a', href=True):
                links.append(a['title'])
            again = False
        except KeyError:
            again = True
            see_also = see_also.find_next('ul')
        except AttributeError:
            again = True
            see_also = see_also.find_next('ul')
    return links


# Function that handles the Wikipedia Search
def wiki_search(subject):
    search = True
    for name in links_dictionary:
        if subject == name:
            search = False
            break
    if search:
        wiki = wikipedia.search(subject)
        try:
            page = wikipedia.page(wiki[0], None, False, True, False)
            print(page)
            base_url = page.url
            links = see_also_links(base_url)
            links_dictionary[subject] = links
            return links
        except (wikipedia.exceptions.PageError, wikipedia.exceptions.DisambiguationError, KeyError, IndexError):
            print('error')
    else:
        pass


# Based on the depth given by the user, this function runs recursively to track down each link
def recursive_search(main_subject, deep):
    link_list = wiki_search(main_subject)
    if (deep > 0) and link_list:
        for link in link_list:
            recursive_search(link, deep-1)


# Main function that starts the whole program
if __name__ == '__main__':
    subject_array = (input('Please Enter the Main Subjects you want to look for (use commas to separate):\n'))
    depth = int(input('What is the maximum depth you\'d like to search to?\n'))
    subject_input = subject_array.split(', ')
    print(subject_input)

    for i in subject_input:
        recursive_search(i, depth)

    G = nx.DiGraph(links_dictionary)
    nx.write_gexf(G, "test.gexf")
