from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

def init_db():
    with sqlite3.connect("recipes.db") as conn:
        with open("schema.sql", "r") as f:
            conn.executescript(f.read())


def get_db_connection():
    conn = sqlite3.connect('recipes.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    recipes = conn.execute('SELECT * FROM recipes ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('index.html', recipes=recipes)

@app.route('/recipe/new', methods=['GET', 'POST'])
def new_recipe():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
        prep_time = request.form['prep_time']
        cook_time = request.form['cook_time']
        servings = request.form['servings']

        if not title or not ingredients or not instructions:
            flash('Title, ingredients, and instructions are required!')
            return redirect(url_for('new_recipe'))

        conn = get_db_connection()
        conn.execute('INSERT INTO recipes (title, description, ingredients, instructions, prep_time, cook_time, servings) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (title, description, ingredients, instructions, prep_time, cook_time, servings))
        conn.commit()
        conn.close()
        flash('Recipe created successfully!')
        return redirect(url_for('index'))

    return render_template('new_recipe.html')

@app.route('/recipe/<int:id>')
def view_recipe(id):
    conn = get_db_connection()
    recipe = conn.execute('SELECT * FROM recipes WHERE id = ?', (id,)).fetchone()
    conn.close()
    if recipe is None:
        flash('Recipe not found!')
        return redirect(url_for('index'))
    return render_template('view_recipe.html', recipe=recipe)

@app.route('/recipe/<int:id>/edit', methods=['GET', 'POST'])
def edit_recipe(id):
    conn = get_db_connection()
    recipe = conn.execute('SELECT * FROM recipes WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
        prep_time = request.form['prep_time']
        cook_time = request.form['cook_time']
        servings = request.form['servings']

        if not title or not ingredients or not instructions:
            flash('Title, ingredients, and instructions are required!')
        else:
            conn.execute('UPDATE recipes SET title = ?, description = ?, ingredients = ?, instructions = ?, prep_time = ?, cook_time = ?, servings = ? WHERE id = ?',
                        (title, description, ingredients, instructions, prep_time, cook_time, servings, id))
            conn.commit()
            flash('Recipe updated successfully!')
            return redirect(url_for('view_recipe', id=id))

    conn.close()
    if recipe is None:
        flash('Recipe not found!')
        return redirect(url_for('index'))
    return render_template('edit_recipe.html', recipe=recipe)

@app.route('/recipe/<int:id>/delete', methods=['POST'])
def delete_recipe(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM recipes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Recipe deleted successfully!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)