import requests
from pprint import pprint
from bs4 import BeautifulSoup
import collections
import json

def extract_lyrics(url, word_limit) -> list:
    r = requests.get(url)
    print(f"Fetching url : {url}")
    # print(r.status_code)
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, 'html.parser')
        # find lyrics inside <div data-lyrics-container="true"> with beautiful soup
        all_lyrics = soup.find_all('div', {'data-lyrics-container': 'true'}, recursive=True)

        phrases = []
        mots_exclues = []
        for lyrics in all_lyrics:
            for line in lyrics.stripped_strings: #stripped_strings permet de supprimer les balises html et récupérer chaque ligne
                for word in line.split(): #split permet de séparer les mots par espace
                    word = word.strip(" .,").lower() #strip permet de supprimer les caractères spécifiés et lower permet de mettre en minuscule
                    word = word.replace("(", "").replace(")", "").replace('"', '') #on enlève les parenthèses et les doubles guillemets
                    if (len(word) > word_limit) and (not (word.startswith("[") or word.endswith("]"))): #on exclut les mots de moins de (word_limit) lettres et les mots entre crochets
                        phrases.append(word)
                    else:
                        mots_exclues.append(word)
        return phrases

    else:
        print('Error')
        return []


def get_all_urls(id_artist):
    page = 1
    links = []
    print(f'\nGetting all urls for artist {id_artist}')
    while True:
        print(f'Getting page {page}')
        r = requests.get(f'https://genius.com/api/artists/{id_artist}/songs?page={page}&sort=popularity')
        if r.status_code == 200:
            next_page = r.json()['response']['next_page']

            songs = r.json()['response']['songs']
            for song in songs:
                url = song.get('url')
                links.append(url)
                #print(f"url : {url}")

            page+=1

            if not next_page:
                print('No more pages\n')
                break
        else:
            print('\nErreur\n')
            break    
    return links


def get_all_words(id_artist, word_limit):
    urls = get_all_urls(id_artist)
    # pprint(urls)
    words = []
    for url in urls: #analyse toutes les chansons, on peut limiter à 10 par exemple avec urls[:10]
        lyrics = extract_lyrics(url, word_limit)
        words.extend(lyrics)

    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(words, file, indent=4)

    counter = collections.Counter(words)
    print("\n********************************* Les 10 mots les plus utilisés sont : *********************************")
    pprint(counter.most_common(10))
    #pprint(words)


def settings():
    while True:
        choix = str(input("Choisissez un artiste : \n1. Francis Cabrel\n2. Patrick Bruel\n3. Stromae\n4. M. Pokora\n5. Michel Sardou\n"))
        
        #vérifie si c'est un des chiffres avant de convertir en int
        if choix == "1":
            id_artist = 63068
            break
        elif choix == "2":
            id_artist = 29743
            break
        elif choix == "3":
            id_artist = 1484
            break
        elif choix == "4":
            id_artist = 8433
            break
        elif choix == "5":
            id_artist = 41749
            break
        else:
            print("\nErreur, veuillez choisir un chiffre entre 1 et 5\n")
            continue

    while True:
        word_limit = str(input("\nEntrez le nombre de lettres minimum pour les mots à conserver : (5 recommandé)\n"))

        #vérifie si c'est un chiffre avant de convertir en int
        if word_limit.isdigit():
            word_limit = int(word_limit)
            get_all_words(id_artist, word_limit)
            break
        else:
            print("\nErreur, veuillez entrer un chiffre\n")
            continue

settings()