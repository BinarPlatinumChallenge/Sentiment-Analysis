# Sentiment Analysis on Twitter

To run the project, please follow these steps: 
<br>

> ### Create python environment 
<br>
After project cloned, you have to create env.

- MacOs
```
python3 -m venv venv
```

- Windows
```
 py -3 -m venv venv
```
<br>

> ### Activate python environment 
<br> 
In order to activate the corresponding environment, you can use below script

- MacOs
```
. venv/bin/activate
```

- Windows
```
venv\Scripts\activate
```
<br>

> ### Install packages 
<br>

Then install all required packages:
```
pip install `required packages`
```
If your python's version is 3, we suggest using `pip3 install` instead of `pip install`
<br>
<br>

> ### Create folders
<br>
Before you start the project, you have to make 3 folders

`downloads` 
: save all processed files\
`uploads` 
: save all files which users uploaded\
`db`
: save sqllite file
<br>
<br>

> ### Run project
<br>

To start the project:
```
python app.py
```

If you have problem and use Python 3 when you start the project, try this command
``` python
python3 app.py
```

## API
> Open [http://localhost:5000/docs](http://localhost:5000/docs) to see API to predict sentiment