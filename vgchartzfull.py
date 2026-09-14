import traceback

from bs4 import BeautifulSoup, element
from urllib import request
import pandas as pd
import numpy as np

pages = 68 #qtde de páginas a serem processadas em 04/2026
rec_count = 0
rank = []
gname = []
platform = []
year = []
genre = []
critic_score = []
user_score = []
publisher = []
developer = []
sales_na = []
sales_pal = []
sales_jp = []
sales_ot = []
sales_gl = []
release_date = []
last_update = []

columns = {
    'Rank': rank,
    'Name': gname,
    'Platform': platform,
    'Year': year,
    'Genre': genre,
    'Critic_Score': critic_score,
    'User_Score': user_score,
    'Publisher': publisher,
    'Developer': developer,
    'NA_Sales': sales_na,
    'PAL_Sales': sales_pal,
    'JP_Sales': sales_jp,
    'Other_Sales': sales_ot,
    'Global_Sales': sales_gl,
    'Release_Date': release_date,
    'Last_Update': last_update
}

#conteudo original abaixo:
#urlhead = 'https://www.vgchartz.com/gamedb/?page='
#urltail = '&console=&region=All&developer=&publisher=&genre=&boxart=Both&ownership=Both'
#urltail += '&results=1000&order=Sales&showtotalsales=0&showtotalsales=1&showpublisher=0'
#urltail += '&showpublisher=1&showvgchartzscore=0&shownasales=1&showdeveloper=1&showcriticscore=1'
#urltail += '&showpalsales=0&showpalsales=1&showreleasedate=1&showuserscore=1&showjapansales=1'
#urltail += '&showlastupdate=0&showothersales=1&showgenre=1&sort=GL'

#Pesquisa realiaza em 18/04/2026
#https://www.vgchartz.com/games/games.php?page=
# &order=Sales&ownership=Both&direction=DESC
# &showtotalsales=1&shownasales=1&showpalsales=1
# &showjapansales=1&showothersales=1&showpublisher=1
# &showdeveloper=1&showreleasedate=1&showlastupdate=1
# &showvgchartzscore=1&showcriticscore=1&showuserscore=1&showshipped=1

#nova construção da URL
urlhead = 'https://www.vgchartz.com/games/games.php?page='
urltail = '&results=1000&order=Sales&ownership=Both&direction=DESC'
urltail += '&showtotalsales=1&shownasales=1&showpalsales=1'
urltail += '&showjapansales=1&showothersales=1&showpublisher=1'
urltail += '&showdeveloper=1&showreleasedate=1&showlastupdate=1'
urltail += '&showvgchartzscore=1&showcriticscore=1&showuserscore=1&showshipped=1'

for page in range(1, pages):
    print(f"Page: {page}")

    # if page <= 53:
    #     rec_count = 53000
    #     continue

    surl = urlhead + str(page) + urltail
    r = request.urlopen(surl).read()
    print(surl)
    
    soup = BeautifulSoup(r, "html.parser")

    # vgchartz website is really weird so we have to search for
    # <a> tags with game urls
    game_tags = [tag for tag in soup.find_all("a", href=True)
                 if tag['href'].startswith('https://www.vgchartz.com/game/')][0:]
    
    
    for tag in game_tags:
        # if rec_count + 1 <= 53000:  # Skip records until we reach the desired starting point
        #     rec_count += 1
        #     continue

        # add name to list  // NOME DO JOGO fica na variavel GNAME
        gname.append(" ".join(tag.string.split()))
        print(f"{page} - {rec_count + 1} Fetch data for game {gname[-1]}")

        # get different attributes
        # traverse up the DOM tree
        data = tag.parent.parent.find_all("td")

        try:
            sRank = data[0].string
        except Exception as e:
            sRank = np.nan
            print(f"Error fetching data for game {gname[-1]} - RANK - ERRO: {e}")
        rank.append(sRank)
        
        try:
            sPlataform = data[3].find('img').attrs['alt']
        except Exception as e:
            sPlataform = np.nan
            print(f"Error fetching data for game {gname[-1]} - PLATFORM - ERRO: {e}")
        platform.append    (sPlataform)

        try:
            sPublisher = data[4].string
        except Exception as e:
            sPublisher = np.nan
            print(f"Error fetching data for game {gname[-1]} - PUBLISHER - ERRO: {e}")
        publisher.append   (sPublisher)
        
        try:
            sDeveloper = data[5].string
        except Exception as e:
            sDeveloper = np.nan
            print(f"Error fetching data for game {gname[-1]} - DEVELOPER - ERRO: {e}")
        developer.append   (sDeveloper)

        try:
            sCriticScore = data[6].string
        except Exception as e:
            sCriticScore = np.nan
            print(f"Error fetching data for game {gname[-1]} - CRITIC SCORE - ERRO: {e}")
        critic_score.append((sCriticScore) if not sCriticScore.startswith("N/A") else np.nan)

        try:
            sUserScore = data[7].string
        except Exception as e:
            sUserScore = np.nan
            print(f"Error fetching data for game {gname[-1]} - USER SCORE - ERRO: {e}")
        user_score.append  ((sUserScore) if not sUserScore.startswith("N/A") else np.nan)

        try:
            sSalesNA = data[9].string[:-1]
        except Exception as e:
            sSalesNA = np.nan
            print(f"Error fetching data for game {gname[-1]} - NA SALES - ERRO: {e}")
        sales_na.append    ((sSalesNA) if not sSalesNA.startswith("N/A") else np.nan)

        try:
            sSalesPAL = data[10].string[:-1]
        except Exception as e:
            sSalesPAL = np.nan
            print(f"Error fetching data for game {gname[-1]} - PAL SALES - ERRO: {e}")
        sales_pal.append   ((sSalesPAL) if not sSalesPAL.startswith("N/A") else np.nan)

        try:
            sSalesJP = data[11].string[:-1]
        except Exception as e:
            sSalesJP = np.nan
            print(f"Error fetching data for game {gname[-1]} - JP SALES - ERRO: {e}")
        sales_jp.append    ((sSalesJP) if not sSalesJP.startswith("N/A") else np.nan)

        try:
            sSalesOT = data[12].string[:-1]
        except Exception as e:
            sSalesOT = np.nan
            print(f"Error fetching data for game {gname[-1]} - OTHER SALES - ERRO: {e}")
        sales_ot.append    ((sSalesOT) if not sSalesOT.startswith("N/A") else np.nan)
        
        try:
            sSalesGL = data[13].string[:-1]
        except Exception as e:
            sSalesGL = np.nan
            print(f"Error fetching data for game {gname[-1]} - GLOBAL SALES - ERRO: {e}")
        sales_gl.append    ((sSalesGL) if not sSalesGL.startswith("N/A") else np.nan)

        try:
            sReleaseDate = data[15].string
        except Exception as e:
            sReleaseDate = np.nan
            print(f"Error fetching data for game {gname[-1]} - RELEASE DATE - ERRO: {e}")
        release_date.append((sReleaseDate) if sReleaseDate and not sReleaseDate.startswith("N/A") else np.nan)

        try:
            sLastUpdate = data[16].string
        except Exception as e:
            sLastUpdate = np.nan
            print(f"Error fetching data for game {gname[-1]} - LAST UPDATE - ERRO: {e}")
        last_update.append ((sLastUpdate) if sLastUpdate and not sLastUpdate.startswith("N/A") else np.nan)
        
        try:
            sReleaseYear = data[15].string.split()[-1]
        except Exception as e:
            sReleaseYear = np.nan
            print(f"     Error fetching data for game {gname[-1]} - RELEASE YEAR - ERRO: {e}")
        release_year = sReleaseYear if sReleaseYear and not sReleaseYear.startswith("N/A") else np.nan
        # different format for year
        year.append(release_year)
        # if release_year != np.nan and release_year != "N/A":
            # if int(release_year) >= 80:
            #     year_to_add = ("19" + release_year)
            # else:
            #     year_to_add = ("20" + release_year)
            # year.append(year_to_add)
        # else:
            # year.append(np.nan)

        # go to every individual website to get genre info
        url_to_game = tag.attrs['href']

        try:
            site_raw = request.urlopen(url_to_game).read()
            sub_soup = BeautifulSoup(site_raw, "html.parser")
            # again, the info box is inconsistent among games so we
            # have to find all the h2 and traverse from that to the genre name
            h2s = sub_soup.find("div", {"id": "gameGenInfoBox"}).find_all('h2')
            # make a temporary tag here to search for the one that contains
            # the word "Genre"
            temp_tag = element.Tag
            for h2 in h2s:
                if h2.string == 'Genre':
                    temp_tag = h2
            genre.append(temp_tag.next_sibling.string)

        except Exception as e:
            print(f"     Error fetching genre data for game {gname[-1]} - ERRO: {e}")
            genre.append("NÃO CAPTURADO")

        if len(rank) != (rec_count%100)+1 or len(gname) != (rec_count%100)+1 or len(platform) != (rec_count%100)+1 or len(year) != (rec_count%100)+1 or len(genre) != (rec_count%100)+1 or len(publisher) != (rec_count%100)+1 or len(developer) != (rec_count%100)+1 or len(critic_score) != (rec_count%100)+1 or len(user_score) != (rec_count%100)+1 or len(sales_na) != (rec_count%100)+1 or len(sales_pal) != (rec_count%100)+1 or len(sales_jp) != (rec_count%100)+1 or len(sales_ot) != (rec_count%100)+1 or len(sales_gl) != (rec_count%100)+1 or len(release_date) != (rec_count%100)+1 or len(last_update) != (rec_count%100)+1:
            print(f"     Data inconsistency detected at record {rec_count + 1}. Check the data lists.")
            print(f"     Rank count: {len(rank)}, Name count: {len(gname)}, Platform count: {len(platform)}, Year count: {len(year)}, Genre count: {len(genre)}, Publisher count: {len(publisher)}, Developer count: {len(developer)}, Critic Score count: {len(critic_score)}, User Score count: {len(user_score)}, NA Sales count: {len(sales_na)}, PAL Sales count: {len(sales_pal)}, JP Sales count: {len(sales_jp)}, Other Sales count: {len(sales_ot)}, Global Sales count: {len(sales_gl)}, Release Date count: {len(release_date)}, Last Update count: {len(last_update)}")
            raise ValueError("Data inconsistency detected. Check the data lists.")

        rec_count += 1
        if rec_count % 100 == 0:
            print(f"Processed {rec_count} records. Gravando arquivo parcial...")
            df = pd.DataFrame(columns)
            df = df[[
                'Rank', 'Name', 'Platform', 'Year', 'Genre',
                'Publisher', 'Developer', 'Critic_Score', 'User_Score',
                'NA_Sales', 'PAL_Sales', 'JP_Sales', 'Other_Sales', 'Global_Sales', 'Release_Date', 'Last_Update']]
            df.to_csv(f"vgsales_partial_{rec_count}.csv", sep=",", encoding='utf-8', index=False)
            for lista in columns.values():
                lista.clear()

if rec_count % 100 != 0:
    print(rec_count)
    df = pd.DataFrame(columns)
    print(df.columns)
    df = df[[
        'Rank', 'Name', 'Platform', 'Year', 'Genre',
        'Publisher', 'Developer', 'Critic_Score', 'User_Score',
        'NA_Sales', 'PAL_Sales', 'JP_Sales', 'Other_Sales', 'Global_Sales', 'Release_Date', 'Last_Update']]
    df.to_csv("vgsales.csv", sep=",", encoding='utf-8', index=False)

print("Processamento concluído. Total de registros processados:", rec_count)
