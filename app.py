from flask import Flask, request, render_template_string

app = Flask(__name__)

# Define the template with the form
html_template = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Movie Rating</title>
  </head>
  <body>
    <h1>Rate Movies</h1>
    <form method="POST" action="/submit">
      {% for i in range(1, 101) %}
        <div>
          <img src="https://liangfgithub.github.io/MovieImages/{{ i }}.jpg" alt="Movie {{ i }}" style="width:100px;height:150px;">
          <label for="movie_{{ i }}">Rate (1-5):</label>
          <input type="number" id="movie_{{ i }}" name="movie_{{ i }}" min="1" max="5" required>
        </div>
      {% endfor %}
      <button type="submit">Submit Ratings</button>
    </form>
  </body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(html_template)

@app.route('/submit', methods=['POST'])
def submit():
    ratings = {key: request.form[key] for key in request.form}
    response_message = "Ratings submitted successfully!"
    return f"<h1>{response_message}</h1><pre>{ratings}</pre>"

if __name__ == "__main__":
    app.run(debug=True)