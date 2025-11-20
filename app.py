# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super-secret-key'  # For flash messages

DATA_FILE = 'data.json'

# Default data structure
DEFAULT_DATA = {
    "config": {
        "name": "Your Name",
        "course_number": "CS101",
        "course_description": "Introduction to Web Development",
        "profile_info": "I'm a passionate developer learning Flask and building portfolios."
    },
    "projects": []
}

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump(DEFAULT_DATA, f, indent=4)
        return DEFAULT_DATA
    
    try:
        with open(DATA_FILE, 'r') as f:
            content = f.read().strip()
            if not content:
                # File is empty
                with open(DATA_FILE, 'w') as f2:
                    json.dump(DEFAULT_DATA, f2, indent=4)
                return DEFAULT_DATA
            return json.loads(content)
    except json.JSONDecodeError:
        # Corrupted JSON - reset to default
        print("data.json was corrupted. Resetting to default.")
        with open(DATA_FILE, 'w') as f:
            json.dump(DEFAULT_DATA, f, indent=4)
        return DEFAULT_DATA

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    data = load_data()
    return render_template('index.html', config=data['config'], projects=data['projects'])

@app.route('/config', methods=['GET', 'POST'])
def config():
    data = load_data()
    if request.method == 'POST':
        data['config']['name'] = request.form['name']
        data['config']['course_number'] = request.form['course_number']
        data['config']['course_description'] = request.form['course_description']
        data['config']['profile_info'] = request.form['profile_info']
        save_data(data)
        flash('Configuration updated successfully!', 'success')
        return redirect(url_for('config'))
    return render_template('config.html', config=data['config'])

@app.route('/project/add', methods=['GET', 'POST'])
def add_project():
    data = load_data()
    if request.method == 'POST':
        project = {
            "id": int(datetime.now().timestamp() * 1000),
            "image": request.form['image'],
            "title": request.form['title'],
            "website_url": request.form['website_url'],
            "github_url": request.form['github_url'],
            "description": request.form['description']
        }
        data['projects'].append(project)
        save_data(data)
        flash('Project added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_project.html')

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    data = load_data()
    project = next((p for p in data['projects'] if p['id'] == project_id), None)
    if not project:
        flash('Project not found!', 'danger')
        return redirect(url_for('index'))
    return render_template('project_detail.html', project=project)

@app.route('/project/edit/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    data = load_data()
    project = next((p for p in data['projects'] if p['id'] == project_id), None)
    if not project:
        flash('Project not found!', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        project['image'] = request.form['image']
        project['title'] = request.form['title']
        project['website_url'] = request.form['website_url']
        project['github_url'] = request.form['github_url']
        project['description'] = request.form['description']
        save_data(data)
        flash('Project updated successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('edit_project.html', project=project)

@app.route('/project/delete/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    data = load_data()
    data['projects'] = [p for p in data['projects'] if p['id'] != project_id]
    save_data(data)
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)