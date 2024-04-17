from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from bs4 import BeautifulSoup
import requests

basedir = os.path.abspath(os.path.dirname(__file__))  # create the app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
        'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Recipe(db.Model):  # create what the recipe database will look like
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    ingredients = db.Column(db.String(500))
    directions = db.Column(db.String(1000))
    tags = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<Recipe {self.id}-{self.title} >'

def scrape(s):
    html = requests.get(s)
    soup = BeautifulSoup(html.text, "html.parser")  # make a beautiful soup object
    recipe_list = []
    for link in soup.find_all('a'):
        if("https://www.onceuponachef.com/recipes/" in link.get('href')):
            recipe_list.append(link.get('href'))
    recipe_list = recipe_list[23:-1]
    for item in recipe_list:
        html = requests.get(item)
        soup = BeautifulSoup(html.text, "html.parser")
        if soup.find('h2', {'class': "fn tabtitle"}) is None:
            return
        else:
            title = soup.find('h2', {'class': "fn tabtitle"}).text
        title = title.lower()
        print(title)
        ingredients = soup.find_all('li', {'class': "ingredient"})
        ingredient_dict = {}
        for item in ingredients:
            if item.find('span', {'class': 'amount'}) is None:
                ingredient_dict[''] = item.find('span', {'class': 'name'}).text
            else:
                ingredient_dict[item.find('span', {'class': 'amount'}).text] = item.find('span', {'class': 'name'}).text
        ingredients = ""
        for amount, ingredient in ingredient_dict.items():
            ingredients += (f"{amount} {ingredient}, ")
        ingredients = ingredients.lower()
        direction = soup.find_all('li', {'class': 'instruction'})
        directions = ''
        for item in direction:
            directions += item.text
        directions = directions.lower()
        new_recipe(title=title, ingredients=ingredients, directions=directions,tags="")

@app.get('/')
def home():  # the home page of the web app (will have all the recipes on it)
    recipe_list = db.session.query(Recipe).all()
    for recipe in recipe_list:
        recipe.title = recipe.title.title()
    return render_template("base.html", recipe_list =recipe_list)

@app.post('/add')
def add():
    title = request.form.get("title")  # get all the info that the user entered and make it lowercase
    title = title.lower()
    ingredients = request.form.get("ingredients")
    ingredients = ingredients.lower()
    directions = request.form.get("directions")
    directions = directions.lower()
    tags = request.form.get("tags")
    tags = tags.lower()
    new_recipe(title, ingredients, directions, tags)


def new_recipe(title, ingredients, directions, tags):
    dairy_list = ["milk","butter","cheese","yogurt","heavy cream", "sour cream"]
    meat_list = ["meat","chicken","duck","turkey","ribs","deli","beef","lamb"]
    vegan_list =["mayo", "eggs", "fish", "tuna", "salmon"]
    for item in dairy_list:  
        if item in ingredients:  # if there's something dairy add dairy to the tags
            tags += ", dairy"
    for item in meat_list:  # if meat is in ingredients add meat to tag
        if item in ingredients:
            tags += ", meat"
    if("dairy"not in tags) and ("meat" not in tags):  
        flag = 0
        for item in vegan_list:
            if item in ingredients:  # if nothing meat dairy or on vegan no-list then add vegan to tags
                flag += 1
        if flag == 0:
            tags += ", vegan"
    recipe = Recipe(title=title, ingredients=ingredients, directions=directions, tags=tags)  # create a new row/recipe in the db=user info
    db.session.add(recipe)
    db.session.commit()  
    return redirect(url_for("home"))  # return to the home page

@app.post('/search')
def search():  # get the user's search and check if it's part of the title, ingredients, or tag
    search = request.form.get("search")
    search = search.lower()
    search_response = []  # create a list for all the recipes that have the search in it
    search_response.append(db.session.query(Recipe).filter(search in Recipe.title).all())
    search_response.append(db.session.query(Recipe).filter(search in Recipe.ingredients).all())
    search_response.append(db.session.query(Recipe).filter(search in Recipe.tags).all())
    return render_template("search.html", search_response=search_response, search=search)  # open a new page of html for the searches


@app.get("/view/<int:recipe_id>")
def view(recipe_id):  # view a recipe that a user clicked on
    recipe = db.session.query(Recipe).filter(Recipe.id == recipe_id).first()
    db.session.commit()
    recipe_viewer = f"{recipe.ingredients}\n\n{recipe.directions}"  # print out the recipe
    recipe.title = recipe.title.title()
    return render_template("view_recipe.html", recipe=recipe, recipe_viewer=recipe_viewer)


@app.post('/<int:recipe_id>/delete/')  # delete a recipe
def delete(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    db.session.delete(recipe)
    db.session.commit()
    return redirect(url_for("home"))

if __name__ == "__main__":
    
    # scrape("https://www.onceuponachef.com/recipes/dinner")
    app.run(host='0.0.0.0', threaded=True, debug=False)
    

