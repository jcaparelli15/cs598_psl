from flask import Flask, request, render_template_string
import pandas as pd
import numpy as np

app = Flask(__name__)
header = pd.read_csv('headers.csv', index_col=0).columns.tolist()
sim_matrix = pd.read_csv('s_filtered.csv', index_col=0)
html_template = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Movie Rating</title>
    <style>
      body {
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
        text-align: center;
      }
      .movie-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 10px;
        padding: 20px;
        max-width: 1000px;
        margin: 0 auto;
      }
      .movie-item {
        padding: 10px;
      }
      img {
        width: 100px;
        height: 150px;
        margin-bottom: 5px;
      }
      button {
        padding: 10px 20px;
        font-size: 16px;
        cursor: pointer;
      }
    </style>
  </head>
  <body>
    <h1>Rate some of the below movies for some recommendations</h1>
    <form method="POST" action="/submit">
      <div class="movie-grid">
        {% for i in range(1, 101) %}
          <div class="movie-item">
            <img src="https://liangfgithub.github.io/MovieImages/{{ i }}.jpg" alt="Movie {{ i }}" style="width:100px;height:150px;">
            <label for="movie_{{ i }}">Rate (1-5):</label>
            <input type="number" id="movie_{{ i }}" name="movie_{{ i }}" min="1" max="5">
          </div>
        {% endfor %}
      </div>
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
    recs = getRecs(ratings)
    response_template = """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Recommendations</title>
    <style>
      body {
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
        text-align: center;
      }
      .movie-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 10px;
        padding: 20px;
        max-width: 1000px;
        margin: 0 auto;
      }
      .movie-item {
        padding: 10px;
      }
      img {
        width: 100px;
        height: 150px;
        margin-bottom: 5px;
      }
      button {
        padding: 10px 20px;
        font-size: 16px;
        cursor: pointer;
      }
    </style>
      </head>
      <body>
        <h1>Ratings submitted successfully!</h1>
        <h2>Recommended Movies:</h2>
        <div class="movie-grid">
          {% for i in recommended_movies %}
            <div class="movie-item">
              <img src="https://liangfgithub.github.io/MovieImages/{{ i }}.jpg" alt="Movie {{ loop.index }}" style="width:100px;height:150px;">
              <p>Movie Recommendation #{{ loop.index }}</p>
            </div>
          {% endfor %}
        </div>
      </body>
    </html>
    """
    return render_template_string(response_template, recommended_movies=recs)
def getRecs(ratings):
    series = pd.Series(data=np.nan, index=[f"m{i}" for i in range(1, 3707)])
    for i, value in enumerate(ratings.values(), start=1):
        series[f"m{i}"] = value
    series.replace('', np.nan, inplace=True)
    series = series.fillna(np.nan)
    series = series.astype(float)
    series = pd.Series(series.values, index=header)
    preds = [int(x[1:]) for x in myIBCF(series)]
    return preds

def predict(j, s, w):
    rated = s.iloc[:, j].dropna().index
    valid_users = rated[w[rated].notna()]
    weighted_users = w[valid_users]
    if len(valid_users) == 0:
        return np.nan
    ratings = s.loc[valid_users, s.columns[j]]
    num = (ratings.fillna(0).to_numpy().flatten() * weighted_users.fillna(0).to_numpy().flatten()).sum()
    denom = weighted_users.sum()
    if denom == 0:
      return np.nan
    return num / denom

def myIBCF(w):
  preds = [predict(j, sim_matrix, w) for j in range(sim_matrix.shape[1])]
  preds_df = pd.DataFrame(preds, index=sim_matrix.columns, columns=['Prediction'])
  preds = preds_df['Prediction'].nlargest(10).index.to_list()
  return [header[int(i)] for i in preds]
if __name__ == "__main__":
    app.run(debug=True)
