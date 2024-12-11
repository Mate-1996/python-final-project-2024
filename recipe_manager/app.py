from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3, os
from functools import wraps
from dotenv import load_dotenv
from cryptography.fernet import Fernet


app = Flask(__name__)
app.secret_key = 'hgfjrtd'

def init_db():
    with sqlite3.connect("recipes.db") as conn:
        with open("schema.sql", "r") as a:
            conn.executescript(a.read())

load_dotenv()
encryption_key = os.getenv('ENCRYPTION_KEY')

# If no key exists, generate one and save it (do this once)
if not encryption_key:
    encryption_key = Fernet.generate_key()
    with open('../.env', 'w') as f:
        f.write(f'ENCRYPTION_KEY={encryption_key.decode()}')




BLOCKED_IPS = {'126.0.0.1'}  # Add IPs you want to block

def check_ip(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.remote_addr in BLOCKED_IPS:
            return jsonify({'error': 'blocked access'}), 403
        return f(*args, **kwargs)
    return wrapper


def get_db_connection():
    conn = sqlite3.connect('recipes.db')
    conn.row_factory = sqlite3.Row
    return conn

fernet = Fernet(encryption_key.encode())

def encrypt_data(data: str) -> str:
    """Encrypt a string"""
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt an encrypted string"""
    return fernet.decrypt(encrypted_data.encode()).decode()

@app.route('/')
def index():
    conn = get_db_connection()
    recipes = conn.execute('SELECT * FROM recipes ORDER BY created_at DESC').fetchall()
    conn.close()
    print(f"Fetched {len(recipes)} recipes from the database.")
    return render_template('index.html', recipes=recipes)

@app.route('/recipe/new', methods=['GET', 'POST'])
@check_ip
def new_recipe():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
        prep_time = request.form['prep_time']
        cook_time = request.form['cook_time']
        servings = request.form['servings']

        print(f"Received data: title={title}, ingredients={ingredients}, instructions={instructions}")

        if not title or not ingredients or not instructions:
            print("Validation error: Missing required fields.")
            flash('Title, ingredients, and instructions are required!')
            return redirect(url_for('new_recipe'))



        conn = get_db_connection()
        print(f"Inserting new recipe: {title}")
        conn.execute('INSERT INTO recipes (title, description, ingredients, instructions, prep_time, cook_time, servings) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (title, description, ingredients, instructions, prep_time, cook_time, servings))
        conn.commit()
        conn.close()
        print("New recipe inserted successfully.")
        flash('Recipe created successfully!')
        return redirect(url_for('index'))

    return render_template('new_recipe.html')


@app.route('/recipe/<int:id>')
def view_recipe(id):
    conn = get_db_connection()
    recipe = conn.execute('SELECT * FROM recipes WHERE id = ?', (id,)).fetchone()
    conn.close()
    if recipe is None:
        print(f"Recipe with ID {id} not found.")
        flash('Recipe not found!')
        return redirect(url_for('index'))
    print(f"Fetched recipe: {recipe['title']}")
    return render_template('view_recipe.html', recipe=recipe)

@app.route('/recipe/<int:id>/edit', methods=['GET', 'POST'])
def edit_recipe(id):
    print(f"Accessing '/recipe/{id}/edit' route to edit a recipe.")
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
            print("Validation error: Missing required fields.")
            flash('Title, ingredients, and instructions are required!')
        else:
            conn.execute('UPDATE recipes SET title = ?, description = ?, ingredients = ?, instructions = ?, prep_time = ?, cook_time = ?, servings = ? WHERE id = ?',
                        (title, description, ingredients, instructions, prep_time, cook_time, servings, id))
            conn.commit()
            print(f"Recipe ID {id} updated successfully.")
            flash('Recipe updated successfully!')
            return redirect(url_for('view_recipe', id=id))

    conn.close()
    if recipe is None:
        print(f"Recipe with ID {id} not found.")
        flash('Recipe not found!')
        return redirect(url_for('index'))
    return render_template('edit_recipe.html', recipe=recipe)

@app.route('/recipe/<int:id>/delete', methods=['POST'])
def delete_recipe(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM recipes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    print(f"Recipe ID {id} deleted successfully.")
    flash('Recipe deleted successfully!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)