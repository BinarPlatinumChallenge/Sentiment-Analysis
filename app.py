import sqlite3
import pickle
import os
import pandas as pd
import pickle5 as pickle5
import numpy as np
import uuid

from datetime import datetime
from keras.models import load_model
from werkzeug.utils import secure_filename
from tensorflow.keras.preprocessing.sequence import pad_sequences
from flask import Flask, send_file, flash, redirect, jsonify, request
from flasgger import LazyJSONEncoder, LazyString, Swagger, swag_from
from cleansing import cleanse_text

UPLOAD_FOLDER = './uploads'
DOWNLOAD_FOLDER = './downloads'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.json_encoder = LazyJSONEncoder
swagger_template = dict(
    info = {
      'title':  LazyString(lambda: 'Sentiment Predict'),
      'version':  LazyString(lambda: '1.0.0'),
      'description': LazyString(lambda: 'API Documentation for sentiment predict')
    },
    host = LazyString(lambda: request.host) 
)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json'
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}

swagger = Swagger(app, template=swagger_template, config=swagger_config)

#database connection
conn = sqlite3.connect('db/sentiment-analysis.db', check_same_thread=False)
c = conn.cursor()
print('Opened database successfully')

c.execute('''CREATE TABLE IF NOT EXISTS data (uuid text, file text, download_path text, text text, model text, feature_extraction text, sentiment text);''')
print('Table created successfully')

tfidf_feature_file = open('./resources/feature_extraction/tfidf/tf-idf_feature.pickle', 'rb')
tfidf_feature = pickle.load(tfidf_feature_file)
tfidf_feature_file.close()

bow_feature_file = open('./resources/feature_extraction/bow/bow_feature.pickle', 'rb')
bow_feature = pickle.load(bow_feature_file)
bow_feature_file.close()

tfidf_model_file = open('./resources/model/nn/tfidf_model.pickle', 'rb')
tfidf_model = pickle.load(tfidf_model_file)
tfidf_model_file.close()

bow_model_file = open('./resources/model/nn/bow_model.pickle', 'rb')
bow_model = pickle.load(bow_model_file)
bow_model_file.close()

tokenizer_file = open('./resources/feature_extraction/tokenizer/tokenizer.pickle', 'rb')
tokenizer = pickle.load(tokenizer_file)
tokenizer_file.close()

pad_sequences_file = open('./resources/feature_extraction/pad_sequence/x_pad_sequences.pickle', 'rb')
X = pickle.load(pad_sequences_file)
pad_sequences_file.close()

lstm_model = load_model('./resources/model/lstm/model.h5')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def getNNSentiment(cleaned_text: str, option: str):
    feature_extraction = tfidf_feature if option == 'TF-IDF' else bow_feature
    model = tfidf_model if option == 'TF-IDF' else bow_model
    text_transform = feature_extraction.transform([cleaned_text])
    sentiment = model.predict(text_transform)[0]
    return sentiment

def getLSTMSentiment(cleaned_text: str):
    print(cleaned_text)
    option = ['negative', 'neutral', 'positive']
    predicted = tokenizer.texts_to_sequences([cleaned_text])
    guess = pad_sequences(predicted, maxlen=X.shape[1])
    prediction = lstm_model.predict(guess)
    polarity = np.argmax(prediction[0])
    sentiment = option[polarity]
    return sentiment

@swag_from('docs/lstm_text.yml', methods=['POST'])
@app.route('/lstm_text', methods=['POST'])
def lstm_sentiment_prediction():
    text = request.form.get('text')
    cleaned_text = cleanse_text(text)
    sentiment = getLSTMSentiment(cleaned_text)
    json_response = {
        'status_code': 200,
        'description': 'Sentiment Prediction',
        'text': text,
        'cleaned_text': cleaned_text,
        'sentiment': sentiment
    }
    response_data = jsonify(json_response)
    c.execute("INSERT INTO data (uuid, text, model, sentiment) values(?,?,?,?)",(str(uuid.uuid4()), text, 'LSTM', sentiment)) 
    conn.commit()
    return response_data

@swag_from('docs/nn_text.yml', methods=['POST'])
@app.route('/nn_text', methods=['POST'])
def nn_sentiment_prediction():
    text = request.form.get('text')
    option = request.form.get('feature_extraction')
    cleaned_text = cleanse_text(text)
    sentiment = getNNSentiment(cleaned_text, option)
    json_response = {
        'status_code': 200,
        'description': 'Sentiment Prediction',
        'feature_extraction': option,
        'text': text,
        'sentiment': sentiment
    }
    response_data = jsonify(json_response)
    c.execute("INSERT INTO data (uuid, text, model, feature_extraction, sentiment) values(?, ?,?,?,?)",(str(uuid.uuid4()), text, 'Neural Network', option, sentiment)) 
    conn.commit()
    return response_data

@swag_from('docs/nn_file.yml', methods=['POST'])
@app.route('/nn_file', methods=['POST'])
def nn_file_sentiment_prediction():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        option = request.form.get('feature_extraction')
        file_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        extension = os.path.splitext(filename)[1]
        filename = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p") + extension
        url_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(url_path)
        df = pd.read_csv(url_path, encoding='latin-1')
        df = df.dropna()
        download_path = os.path.join(app.config['DOWNLOAD_FOLDER'], file_id + extension)
        df['cleaned_text'] = df.iloc[:, 0].apply(cleanse_text)
        df['sentiment'] = df['cleaned_text'].apply(lambda x: getNNSentiment(x, option))
        df.to_csv(download_path, header = True, index=False)
        c.execute('BEGIN TRANSACTION')
        c.execute("INSERT OR IGNORE INTO data (uuid, file, download_path, model, feature_extraction) values(?,?,?,?,?)",(file_id, url_path, download_path, 'Neural Network', option)) 
        c.execute('COMMIT')
        return send_file(download_path, mimetype='text/csv', download_name=file_id + '.csv', as_attachment=True)

@swag_from('docs/lstm_file.yml', methods=['POST'])
@app.route('/lstm_file', methods=['POST'])
def lstm_file_sentiment_prediction():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        file_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        extension = os.path.splitext(filename)[1]
        filename = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p") + extension
        url_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(url_path)
        df = pd.read_csv(url_path, encoding='latin-1')
        df = df.dropna()
        download_path = os.path.join(app.config['DOWNLOAD_FOLDER'], file_id + extension)
        df['cleaned_text'] = df.iloc[:, 0].apply(cleanse_text)
        df['sentiment'] = df['cleaned_text'].apply(getLSTMSentiment)
        df.to_csv(download_path, header = True, index=False)
        c.execute('BEGIN TRANSACTION')
        c.execute("INSERT OR IGNORE INTO data (uuid, file, download_path, model) values(?,?,?,?)",(file_id, url_path, download_path, 'LSTM')) 
        c.execute('COMMIT')
        return send_file(download_path, mimetype='text/csv', download_name=file_id + '.csv', as_attachment=True)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

if __name__ == '__main__':
    app.run(port=5000, debug=True)