import pickle
import pickle5 as pickle5
import numpy as np
from keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from flask import Flask, jsonify, request
from flasgger import LazyJSONEncoder, LazyString, Swagger, swag_from
from cleansing import cleanse_text

app = Flask(__name__)
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

def getFeatureExtractionFile(option):
    feature_extraction_file_name = './resources/feature_extraction/tfidf/tf-idf_feature.pickle' if option == 'TF-IDF' else './resources/feature_extraction/bow/bow_feature.pickle'
    return feature_extraction_file_name

@swag_from('docs/lstm_text.yml', methods=['POST'])
@app.route('/lstm_text', methods=['POST'])
def lstm_sentiment_prediction():
    text = request.form.get('text')
    cleaned_text = cleanse_text(text)
    sentiment = ['negative', 'neutral', 'positive']

    input = [cleaned_text]
    tokenizer_file = open('./resources/feature_extraction/tokenizer/tokenizer.pickle', 'rb')
    tokenizer = pickle5.load(tokenizer_file)
    tokenizer_file.close()

    predicted = tokenizer.texts_to_sequences(input) 
    pad_sequence_file = open('./resources/pad_sequence/x_pad_sequences.pickle','rb')
    feature_file = pickle5.load(pad_sequence_file)
    pad_sequence_file.close()

    guess = pad_sequences(predicted, maxlen=feature_file.shape[1])
    model = load_model('./resources/model/lstm/model.h5')
    prediction = model.predict(guess)
    polarity = np.argmax(prediction[0])

    json_response = {
        'status_code': 200,
        'description': 'Sentiment Prediction',
        'text': text,
        'sentiment': sentiment[polarity]
    }
    response_data = jsonify(json_response)
    return response_data

@swag_from('docs/nn_text.yml', methods=['POST'])
@app.route('/nn_text', methods=['POST'])
def nn_sentiment_prediction():
    text = request.form.get('text')
    option = request.form.get('feature_extraction')
    cleaned_text = cleanse_text(text)

    feature_extraction_file_name = getFeatureExtractionFile(option)
    print(feature_extraction_file_name)
    feature_extraction_file = open(feature_extraction_file_name, 'rb')
    tfidf_fe = pickle.load(feature_extraction_file)
    feature_extraction_file.close()

    model_file = open('./resources/model/nn/model_tfidf.pickle', 'rb')
    model = pickle.load(model_file)
    model_file.close()

    text_transform = tfidf_fe.transform([cleaned_text])
    sentiment = model.predict(text_transform)[0]

    json_response = {
        'status_code': 200,
        'description': 'Sentiment Prediction',
        'feature_extraction': option,
        'text': text,
        'sentiment': sentiment
    }
    response_data = jsonify(json_response)

    # c.execute("INSERT INTO data (original_text, cleaned_text) values(?,?)",(text, cleaned_text)) 
    # conn.commit()
    return response_data

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

if __name__ == '__main__':
    app.run(port=5000, debug=True)