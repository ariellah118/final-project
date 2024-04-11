from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

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

@app.get('/')
def home():  # the home page of the web app (will have all the recipes on it)
    recipe_list = db.session.query(Recipe).all()
    return render_template("base.html", recipe_list =recipe_list)

@app.post('/add')
def add():
    title = request.form.get("title")  # get all the info that the user entered and make it lowercase
    title = title.title()
    ingredients = request.form.get("ingredients")
    ingredients = ingredients.lower()
    directions = request.form.get("directions")
    directions = directions.lower()
    tags = request.form.get("tags")
    tags = tags.lower()
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
    new_recipe = Recipe(title=title, ingredients=ingredients, directions=directions, tags=tags)  # create a new row/recipe in the db=user info
    db.session.add(new_recipe)
    db.session.commit()  
    return redirect(url_for("home"))  # return to the home page

@app.post('/search')
def search():  # get the user's search and check if it's part of the title, ingredients, or tag
    search = request.form.get("search")
    search = search.lower()
    search_response = []  # create a list for all the recipes that have the search in it
    search_response.append(db.session.query(Recipe).filter(search in Recipe.title.lower()).all())
    search_response.append(db.session.query(Recipe).filter(search in Recipe.ingredients).all())
    search_response.append(db.session.query(Recipe).filter(search in Recipe.tags).all())
    return render_template("search.html", search_response=search_response, search=search)  # open a new page of html for the searches

    


#new_recipe = Recipe(title="Baked Apples", ingredients="6 apples, cinnamon", directions="dice apples, sprinkle with cinnamon, and bake on 350 until soft", tags="dessert")

@app.get("/view/<int:recipe_id>")
def view(recipe_id):  # view a recipe that a user clicked on
    recipe = db.session.query(Recipe).filter(Recipe.id == recipe_id).first()
    db.session.commit()
    recipe_viewer = f"{recipe.ingredients}\n\n{recipe.directions}"  # print out the recipe
    return render_template("view_recipe.html", recipe=recipe, recipe_viewer=recipe_viewer)

if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=True, debug=False)
    

