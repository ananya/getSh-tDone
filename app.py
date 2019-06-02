from flask import Flask, request , render_template
from views import videoedit
from views import textsummariser
import json

app = Flask(__name__)

#routes
@app.route('/',methods=['GET','POST'])
def do_landing():
    try:
        return render_template('landing.html')
    except Exception as e:
        return e

@app.route('/home',methods=['GET'])
def do_something():
    try:
        return render_template('index.html')
    except Exception as e:
        return e

@app.route('/videoedit')
def do_something_next():
    try:
        print( videoedit.videoProcess(30,44100,0.03,1,99999,1,None,'omg.mp4','out.mp4',3) )
        return "FUCK U"
    except:
        pass

@app.route('/textsummariser')
def do_text_summariser():
    try:
        return( json.dumps(textsummariser.generate_summary('file.txt',5)) )
    except:
        pass

@app.route('/urlsummariser')
def do_url_summariser():
    try:
        print("neha")
        file_name = textsummariser.convert_url_to_text("https://medium.com/baseds/many-nodes-one-distributed-system-9921f85205c4")
        print ( file_name )
        return( json.dumps(textsummariser.generate_summary(file_name,8) ))
    except:
        pass
        
if __name__ == "main" : 
    app.run(debug=True)