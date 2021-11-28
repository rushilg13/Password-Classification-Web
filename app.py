from flask import Flask, render_template, request, redirect, jsonify
import joblib
import random
import string
import hashlib

app = Flask(__name__)

password_hashmap = {
    '0' : "Weak",
    '1' : "Medium",
    '2' : "Strong" 
}

def password_string_generator(length):
    result = ''.join((random.choice(string.ascii_letters) for x in range(length)))
    for _ in range(length):
        result += random.choice(string.digits)
        result += random.choice(string.punctuation)
    result = ''.join(random.sample(result, len(result)))
    return result

vectorizer = joblib.load("count_vectorizer.pkl")

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template("home.html")

@app.route("/predict", methods=['GET', 'POST'])
def predict():
    pwd = request.form['pwd']
    arr = []
    arr.append(pwd)
    vec_predict = vectorizer.transform(arr)
    model = joblib.load("svm_model_all_data.pkl")
    prediction = model.predict(vec_predict)
    print("Strength is " + prediction)
    return render_template("result.html", prediction = password_hashmap[prediction[0]])

@app.route("/generate", methods=["GET"])
def generate():
    prediction = [-1]
    arr = []
    while int(prediction[0]) != 2:
        generated_password = password_string_generator(6)
        print("Trying... " + generated_password)
        with open('generated_passwords.txt') as f:
            passwords = f.readlines()
            hash_pass = hashlib.sha256(generated_password.encode())
            if hash_pass.hexdigest() in passwords:
                redirect("/generate")
                break
            else:
                arr.append(generated_password)
                vec_predict = vectorizer.transform(arr)
                model = joblib.load("svm_model_all_data.pkl")
                prediction = model.predict(vec_predict)
    print(generated_password, password_hashmap[prediction[0]])
    with open('generated_passwords.txt', 'a') as f:
        f.write(hash_pass.hexdigest() + "\n")
        f.write(generated_password + "\n")
    return redirect("/show_generated")

@app.route("/show_generated", methods=["GET"])
def view_generated():
    with open('generated_passwords.txt', 'r+') as f:
        passwords = f.readlines()
        generated_password = passwords[-1]
        f.seek(0)
        f.truncate()
        f.writelines(passwords[:-1])
    return render_template("generate.html", generated_password = generated_password)

@app.route("/api/<string:password>", methods=['GET'])
def api_get(password):
    pwd = password
    arr = []
    arr.append(pwd)
    vec_predict = vectorizer.transform(arr)
    model = joblib.load("svm_model_all_data.pkl")
    prediction = model.predict(vec_predict)
    print("Strength is " + prediction)
    return jsonify({"Strength": password_hashmap[prediction[0]]})

@app.route("/api", methods=['POST'])
def api_post():
    if request.method == "POST":
        print(request.args.get('password'))
        pwd = request.args.get('password')
        arr = []
        arr.append(pwd)
        vec_predict = vectorizer.transform(arr)
        model = joblib.load("svm_model_all_data.pkl")
        prediction = model.predict(vec_predict)
        print("Strength is " + prediction)
        return jsonify({"Strength": password_hashmap[prediction[0]]})
    else:
        return jsonify({"Message" : "This should be a POST request"})

@app.route("/apis", methods=['GET'])
def api():
    return render_template("api.html")

@app.route("/how", methods=['GET'])
def how():
    return render_template("how.html")

@app.route("/about", methods=['GET'])
def about():
    return render_template("about.html")

if __name__=="__main__":
    app.run(debug=True)
