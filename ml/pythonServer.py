import numpy as np
import pandas as pd
from mal import Anime
import time
import mysql.connector
from flask import Flask, request, jsonify

app = Flask(__name__)

connection = mysql.connector.connect(
     host='database',
     port=3306,
     user='root',
     password='my-secret-pw',
     database='anime'
)



cursor = connection.cursor()


query = "SELECT * FROM anime_for_tags"
cursor.execute(query)
records = cursor.fetchall()
anime_for_tags_data = pd.DataFrame(records, columns=[desc[0] for desc in cursor.description])

query2 = "SELECT * FROM anime_new"
cursor.execute(query)
records = cursor.fetchall()
anime_new_data = pd.DataFrame(records, columns=[desc[0] for desc in cursor.description])


cursor.close()
connection.close()



def recommend_anime_based_on_synopsis(anime_title, amount):
     path = "./cosine_sim.npy"
     cosine_sim = np.load(path)
    
     anime = anime_new_data.copy()
   
     index = anime[anime['Name'] == anime_title].index[0]
     dist = list(enumerate(cosine_sim[index]))
     dist.sort(reverse=True, key=lambda x: x[1])
     return_id = []
     if amount + 1 < len(dist):
         for i in dist[1:amount + 1]:
             return_id.append(anime.iloc[i[0]]['MAL_ID'])
     else:
         for i in dist[1:len(dist) - 1]:
             return_id.append(anime.iloc[i[0]]['MAL_ID'])
     return return_id

    

def searchByTags(tags, searchType):
    returned_anime = anime_for_tags_data.copy()
    for i in tags:
        returned_anime = returned_anime[returned_anime['Genres'].str.contains(i)]
    if(searchType == "Score"):
        returned_anime = returned_anime.sort_values(by='Score', ascending=False)
    else:
        returned_anime['MAL_ID'] = np.random.permutation(returned_anime['MAL_ID'])
    return np.array(returned_anime["MAL_ID"].head(10))

def searchInMAL(arrayOfId):
    animeTitles = []
    animeSynopsis = []
    animeIcons = []
    animeScores = []
    
    for i in range(len(arrayOfId)):
        anime = Anime(arrayOfId[i])
        
        animeTitles.append(anime.title)
        animeScores.append(anime.score)
        animeIcons.append(anime.image_url)
        animeSynopsis.append(anime.synopsis)
        time.sleep(0.5)
        
    data = {'title':animeTitles,'synopsis':animeSynopsis, 'score':animeScores, 'icon':animeIcons}
    return jsonify({'result':data})


def animeNameToId(animeName):
    anime = pd.read_csv("C:/Users/mateu/Desktop/Docker/ml/anime_new.csv")
    row = anime[anime['Name'] == animeName]
    mal_id = row['MAL_ID'].values[0]
    return mal_id

@app.route('/searchByTagsInPython', methods=['POST'])
def tags():
    data = request.json

    searchBy = data['searchingBy']
    oldTags = data['tags']
    tags = [tag.capitalize() for tag in oldTags]
    
    vals = searchByTags(tags=tags , searchType=searchBy)
    return searchInMAL(vals)

@app.route('/searchBySimilaritiesInPython', methods=['POST'])
def synopsis():
    data = request.json
    amount = int(data['amount'])
    animeName = data['animeName']
    animeName = animeName.title()
    vals = recommend_anime_based_on_synopsis(anime_title=animeName, amount=amount)
    return searchInMAL(vals)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)