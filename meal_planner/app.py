from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('database/recipes.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recipes')
def recipes():
    conn = get_db_connection()
    recipes = conn.execute('SELECT * FROM recipes').fetchall()
    conn.close()
    return render_template('recipe.html', recipes=recipes)

@app.route('/add_recipe', methods=('GET', 'POST'))
def add_recipe():
    if request.method == 'POST':
        title = request.form['title']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']

        conn = get_db_connection()
        conn.execute('INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)',
                     (title, ingredients, instructions))
        conn.commit()
        conn.close()
        return redirect(url_for('recipes'))

    return render_template('add_recipe.html')

@app.route('/meal_plan')
def meal_plan():
    return render_template('meal_plan.html')

@app.route('/shopping_list')
def shopping_list():
    return render_template('shopping_list.html')

if __name__ == '__main__':
    app.run(debug=True)


