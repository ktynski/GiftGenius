from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
from ast import literal_eval
import os, time, openai, requests, json, sys, re
from rake_nltk import Rake
import lib.nltk as nltk


app = Flask(__name__)
bootstrap = Bootstrap(app)

openai.api_key = "sk-jtG0RZ5KKrrWXoT86NkI5e29UJHLimzuVzkWNLBa"
completion = openai.Completion()

r = Rake()

# sys.path.append('lib/')
# nltk.data.path.append('lib/nltk_data/')

@app.route('/')
def index():
    return render_template('index.html',name='index')


def getetsy(keyword):
  r.extract_keywords_from_text(keyword)
  nk = r.get_ranked_phrases()

  eurl ="https://openapi.etsy.com/v2/listings/active?keywords="+ nk[0] + "&limit=6&min_price=1&max_price=1000&includes=Images&sort_on=score&api_key=irfd7hodi7rj4mp6yd4hmkqv"
  etsy = requests.get(eurl)
  etsyproduct = etsy.content
  decetsy = etsyproduct.decode('utf-8')
  etsyjson = json.loads(decetsy)
  etsyresult = etsyjson['results']
  return etsyresult

@app.route('/query/',methods=['GET'])
def query():

    if request.method == 'GET':
        query = request.args.get('q') # this is the prompt
        try:
            search_temperature = request.args.get('search_temperature') # 0-10 -> 0.1-1.0
            cast_st = float(search_temperature)

        except:
            cast_st = 6
        search_temperature = cast_st / 10.00

        openai.api_key = "sk-jtG0RZ5KKrrWXoT86NkI5e29UJHLimzuVzkWNLBa"
        gpt3response = openai.Completion.create(
            engine="davinci",
            prompt="This tool is an expert artificial intelligence for predicting great gifts for specific individuals or Personas. For example:\n\n\nPersona: A man in his mid 20's from the midwest. He is conservative and patriotic. He enjoys hunting. He has a lifted truck and is family oriented. He is an avid fisherman and outdoorsman, but also loves a good beer or cigar.\n\nGift Recommendations:\n1. Engraved cigar cutter - To cut the tip off of his cigar without it tearing.\n2. Tactical pen and flashlight - To use if he needs to defend himself while out camping.\n3. American Flag - That can show his pride for America. \n4. Whiskey flask with matching shot glass - To sip his favorite bourbon from when he hunts.\n5. Bullet shaped BBQ lighter - To use while barbequing next to his truck.\n6. Bluetooth tire pressure sensor - To keep up with his tires to ensure he drives safe.\n\nPersona:\n" +query+ ".\n\nGift Recommendations:\n1.",
            temperature=search_temperature,
            max_tokens=100,
            top_p=1,
            frequency_penalty=0.2,
            presence_penalty=1,
            stop=["6."]
        )
        
        productnames = gpt3response.choices[0]['text']
        mystring = productnames 
        removelist = "\n "
        final2 = re.sub (r'[^a-zA-Z'+removelist+']', '', mystring)

        my_list = re.sub(r'[^\w'+removelist+']', '',final2)

        final_list = my_list.split("\n")
        newlst=[]
        for i in final_list:
            if i != " ":
                newlst.append(i[0:])
            else:
                newlst.append(i[1:])

        newlst = [x for x in newlst if x.strip()]

        i = 0
        et= []

         #   print(x)
        #print(newlst)
        ak = []
        for item in newlst:
            et.append(getetsy(item))
            i=i+1
            r.extract_keywords_from_text(item)
            ak.append(r.get_ranked_phrases()[0])

        #print(et)
        #return False
        return render_template("index.html", query=query, results=newlst, et=et)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80,debug = False)
