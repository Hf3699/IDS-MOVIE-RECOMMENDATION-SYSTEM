import requests
from bs4 import BeautifulSoup
import pandas as pd

def GetaSoup(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.999 Safari/537.36'
    }
    page = requests.get(url, headers=headers)
    return BeautifulSoup(page.text, "html.parser")

# Function to scrape data of top films from IMDb
def get_films_data() -> pd.DataFrame:
    soup = GetaSoup('https://www.imdb.com/chart/top/')
    nameArray = []
    genreArray = []
    ratingsArray = []
    releaseyearArray = []
    RealizationArray = []
    actorsArray = []

    tags = soup.find_all("a")
    cleanTags = [i for i in tags if '.' in i.text]  # Filter relevant tags

    for i, value in enumerate(cleanTags):
        name, Realization, actors, genre, ratings, releaseyear = get_film_data(value['href'])
        nameArray.append(name)
        genreArray.append(genre)
        ratingsArray.append(ratings)
        releaseyearArray.append(releaseyear)
        RealizationArray.append(Realization)
        actorsArray.append(actors)
        print(f"Processed film {i + 1}")
        if i == 1000:  # Limit processing to 249 films
            break

    return {"Name": nameArray, "Realisation": RealizationArray, "Actors": actorsArray,
            "Genre": genreArray, "ReleaseYear": releaseyearArray, "Ratings": ratingsArray}

# Helper function to format genres into a comma-separated string
def joinGenre(genre):
    array = []
    ch = ""
    for i, value in enumerate(genre):
        if value.isupper() and i > 0:
            array.append(ch)
            ch = ""
        ch += value
    array.append(ch)
    return ",".join(array)

# Function to fetch the release year from a movie's release date page
def getReleaseData(urlreleaseyear):
    soup = GetaSoup(urlreleaseyear)
    datebyCountry = soup.find("div", {'data-testid': 'sub-section-releases'}).find("ul").find_all('li')
    array = [i.text for i in datebyCountry]
    ch = ''
    for i in array[0]:
        if i != '(':
            ch += i
        else:
            break
    return ch[-4:]

# Function to fetch data for an individual film
def get_film_data(urlToC):
    soup = GetaSoup(f'https://www.imdb.com/{urlToC}')

    # Get name
    name = soup.find("span", {'class': 'hero__primary-text'})
    name = name.text if name else "N/A"

    # Get genre
    genre_element = soup.find("div", {'data-testid': 'genres'})
    genre = genre_element.text if genre_element else "N/A"

    # Get ratings
    ratings_element = soup.find("div", {'data-testid': 'hero-rating-bar__aggregate-rating__score'})
    ratings = ratings_element.text if ratings_element else "N/A"

    # Get director (realisation)
    realization_element = soup.find("li", {'data-testid': 'title-pc-principal-credit'})
    Realization = realization_element.find("a").text if realization_element else "N/A"

    # Get actors
    actors_item = soup.find_all("li", {'data-testid': 'title-pc-principal-credit'})
    if len(actors_item) > 2:
        actors_links = actors_item[2].find_all("a")[1:]
        actors = ",".join(i.text for i in actors_links)
    else:
        actors = "N/A"

    # Get formatted genre
    formattedGenre = joinGenre(genre) if genre != "N/A" else "N/A"

    # Get release year
    release_year_div = soup.find("div", {"class": "sc-e226b0e3-3 dwkouE"})
    if release_year_div:
        release_year_element = release_year_div.find("a", {'class': 'ipc-link ipc-link--baseAlt ipc-link--inherit-color'})
        if release_year_element:
            urlreleaseyear = release_year_element['href']
            ReleaseDate = getReleaseData(f'https://www.imdb.com/{urlreleaseyear}')
        else:
            ReleaseDate = "N/A"
    else:
        ReleaseDate = "N/A"

    return name, Realization, actors[:-1] if actors != "N/A" else "N/A", formattedGenre, ratings, ReleaseDate

# Main script execution
films_data = get_films_data()
data = pd.DataFrame(films_data, columns=films_data.keys())
data.to_csv('data2.csv', index=False)
