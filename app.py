from dotenv import load_dotenv
import os
from os.path import join, dirname
from dotenv import load_dotenv
from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["UPLOAD_FOLDER"] = "./static/profile_pics"

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

SECRET_KEY = 'NOKIA'

@app.route('/')
def index():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"email": payload["id"]})
        return render_template("home.html", user_info=user_info)
    except (jwt.ExpiredSignatureError,jwt.exceptions.DecodeError):
        return redirect(url_for("login", msg="Your token has expired"))
    


@app.route("/login", methods=["GET"])
def login():
    msg = request.args.get("msg")
    return render_template("login.html", msg=msg)

@app.route("/login/enter", methods=["POST"])
def login_enter():
    email_receive = request.form.get("email_give")
    password_receive = request.form.get("password_give")
    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    user=  db.user.find_one({"email": email_receive,"password": pw_hash})
    if user:
        payload = {"id": email_receive,"exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),}
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        print(payload)
        return jsonify({"result": "success","token": token,})
    else:
        return jsonify({"result": "fail","msg": "We could not find a user with that id/password combination",})

@app.route("/signup/save", methods=["POST"])
def signup_save():
    email_receive = request.form['email_give']
    password_receive = request.form['password_give']
    firstName_receive = request.form['firstname_give']
    lastName_receive = request.form['lastname_give']
    village_receive = request.form['village_give']
    Hp_receive = request.form['hp_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "firstName": firstName_receive,
        "lastName": lastName_receive,                             
        "password": password_hash,
        "email": email_receive,
        "role":"pengunjung",
        "village": village_receive,
        "Hp" : Hp_receive,
        "profile_pic_real": "placeholder.svg", 
    }
    db.user.insert_one(doc)
    return redirect(url_for('login'))

@app.route("/signup")
def signup():
    msg = request.args.get("msg")
    return render_template("signup.html", msg=msg)


@app.route("/edit_profile/save", methods=["POST"])
def save_img():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        firstName_receive = request.form['firstName']
        lastName_receive = request.form['lastName']
        village_receive = request.form['address']
        Hp_receive = request.form['phoneNumber']
        doc ={
        "firstName": firstName_receive,
        "lastName": lastName_receive,                             
        "village": village_receive,
        "Hp" : Hp_receive,
        }
        if "Pic" in request.files:
            file = request.files["Pic"]
            print(file)
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"{firstName_receive}.{extension}"
            file.save("./static/" + file_path)
            doc["profile_pic_real"] = file_path
        db.user.update_one({"email": payload["id"]}, {"$set": doc})
        return redirect(url_for("profile"))
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("profile"))


@app.route("/edit-profile")
def editprofile():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"]) 
        user_info = db.user.find_one({"email": payload["id"]})
        return render_template("edit_profile.html", user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route("/profile")
def profile():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"]) 
        user_info = db.user.find_one({"email": payload["id"]})
        print(payload)
        return render_template("profile.html", user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@app.route('/home')
def home():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"email": payload["id"]})
        return render_template("home.html", user_info=user_info)
    except (jwt.ExpiredSignatureError,jwt.exceptions.DecodeError):
        return redirect(url_for("login", msg="Your token has expired"))


@app.route('/aspirasi')
def aspirasi():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"email": payload["id"]})
        return render_template("aspirasi.html", user_info=user_info)
    except (jwt.ExpiredSignatureError,jwt.exceptions.DecodeError):
        return redirect(url_for("login", msg="Your token has expired"))
    

@app.route('/kirimaspirasi')
def kirim_aspirasi():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"]) 
        user_info = db.user.find_one({"email": payload["id"]})
        print(payload)
        return render_template("kirimAspirasi.html", user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


@app.route('/cek_aspirasi')
def cek_aspirasi():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"email": payload["id"]})
        if user_info['role'] == 'pengunjung':
            aspirasi =  list(db.masukan_aspirasi.find({"username":user_info['email']}))
            return render_template("cek_aspirasi.html", user_info=user_info,masukan=aspirasi)
        if user_info['role'] == 'admin':
            aspirasiadmin =  list(db.masukan_aspirasi.find())
            return render_template("cek_aspirasi.html", user_info=user_info,masukanadmin=aspirasiadmin)
        else:
            return redirect(url_for("aspirasi"))
    except (jwt.ExpiredSignatureError,jwt.exceptions.DecodeError):
        return redirect(url_for("login", msg="Your token has expired"))




@app.route('/edit_komunikasi')
def edit_komunikasi():
    return render_template('edit_komunikasi.html')

@app.route('/edit_sosialisasi')
def edit_sosialisasi():
    return render_template('edit_sosialisasi.html')


@app.route('/kirimAspirasi/save',methods=['POST'])
def kirimAspirasi():
    token_receive = request.cookies.get("mytoken")
    try:
        id = db.masukan_aspirasi.count_documents({})
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"email": payload["id"]})
        nama = request.form['nama']
        judul = request.form['judul']
        laporan = request.form['laporan']
        tanggal = request.form['tanggal']
        lokasi = request.form['lokasi']
        kategori = request.form['kategori']
        id += 1
        doc = {
            "id":id,
            "username":user_info['email'],
            "nama":nama,
            "judul":judul,
            "laporan":laporan,
            "tanggal":tanggal,
            "lokasi":lokasi,
            "kategori":kategori,
            "status":"pending",
        }
        db.masukan_aspirasi.insert_one(doc)
        return redirect(url_for("aspirasi"))
    except (jwt.ExpiredSignatureError,jwt.exceptions.DecodeError):
        return redirect(url_for("login", msg="Your token has expired"))
    # ambil data dari form
    
 
@app.route("/aspirasi/confirm", methods=["POST"])
def update_masukan():
    nama = request.form['nama_give']
    db.masukan_aspirasi.update_one({"nama":nama},{"$set":{'status':'Accepted'}})
    return jsonify({"result": "success", "msg": "Masukan Accepted!"})

@app.route("/aspirasi/delete", methods=["POST"])
def delete_masukan():
    nama = request.form['nama_give']
    db.masukan_aspirasi.delete_one({"nama":nama})
    return jsonify({"result": "success", "msg": "Succes Delete"})

@app.route('/api/komunikasi', methods=['POST'])
def send_message():
    
    data = request.get_json()

    if 'message' in data:
        message = data['message']

        # untuk menyimpan message ke mongo db
        aspirasi.messageAspirasi.insert_one({'message': message})
        return jsonify({'success' : True})
    else:
        return jsonify({'success': False, 'error': ' Invalid data'})
    # return render_template('komunikasi.html')


@app.route('/api/komunikasi', methods=['GET'])
def get_message():
    messages = aspirasi.messageAspirasi.find()
    messages_list = [{'message': msg['message']}for msg in messages]

    return jsonify(messages_list)

@app.route('/sosialisasi')
def sosialisasi():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"email": payload["id"]})
        berita =  list(db.berita.find({}))
        return render_template("info.html", user_info=user_info,berita=berita)
    except (jwt.ExpiredSignatureError,jwt.exceptions.DecodeError):
        return redirect(url_for("login", msg="Your token has expired"))


@app.route('/add-sosialisasi',methods=['POST'])
def add_sosialisasi():
    judul_recieve = request.form['judul_give']
    link_recieve = request.form['link_give']
    deskirpsi_recieve = request.form['deskripsi_give']
    if "cover_give" in request.files:
        file = request.files["cover_give"]
        filename = secure_filename(file.filename)
        extension = filename.split(".")[-1]
        file_path = f"{judul_recieve}.{extension}"
        file.save("./static/" + file_path)
    doc = {
        "Judul":judul_recieve,
        "Link":link_recieve,
        "Cover":file_path,
        "Deskripsi":deskirpsi_recieve
    }
    db.berita.insert_one(doc)
    return jsonify({'result': 'success','msg':'Berita Added'})

@app.route('/hapus/berita',methods=['POST'])
def hapusberita():
    judul_recieve = request.form['judul_give']
    db.berita.delete_one({"Judul":judul_recieve})
    return jsonify({'result': 'success','msg':'Berita Deleted'})

@app.route('/komunikasi')
def komunikasi():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"email": payload["id"]})
        return render_template("komunikasi.html", user_info=user_info)
    except (jwt.ExpiredSignatureError,jwt.exceptions.DecodeError):
        return redirect(url_for("login", msg="Your token has expired"))

@app.route('/komunikasi-contoh')
def komunikasi_contoh():
    return render_template('komunikasi_contoh.html')

@app.route('/about')
def about():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"email": payload["id"]})
        return render_template("about.html", user_info=user_info)
    except (jwt.ExpiredSignatureError,jwt.exceptions.DecodeError):
        return redirect(url_for("login", msg="Your token has expired"))

@app.route('/tabel-aspirasi')
def tabel_aspirasi():
    return render_template('tabel_aspirasi.html')


@app.route('/demo')
def demo():
    return render_template('home_demo.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=8002, debug=True)