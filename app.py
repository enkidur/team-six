from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('mongodb+srv://test:sparta@cluster0.ezd2jb5.mongodb.net/?retryWrites=true&w=majority')
db = client.teamsix


@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_status = payload["id"]  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False
        return render_template('main_page.html', info_user=user_status, my_content='not')
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))



@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/main')
def main_page():
    return render_template('main_page.html', my_content='not')


@app.route('/input')
def input():
    return render_template("/input.html")


@app.route('/mypage')
def mypage():
    return render_template("/main_page.html", my_content='not')


@app.route('/community')
def community():
    return render_template("/main_page.html", my_content='on_community')


@app.route('/show')
def show_page():
    return render_template('showpage.html')

@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    # 암호화 진행
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'id': username_receive, 'pw': pw_hash})

    if result is not None:
        # jwt(제이슨 웹 토큰) 발행
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# - db up & load
#########################################################################################################

# 회원가입부분
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    nickname_receive = request.form['nickname_give']
    email_receive = request.form['email_give']
    address_receive = request.form['address_give']
    phone_receive = request.form['phone_give']
    sex_receive = request.form['sex_give']
    birth_receive = request.form['birth_give']
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()

    # 서버 저장하는 부분
    doc = {
        "id": username_receive,  # 아이디 정보
        "pw": password_hash,  # 비밀번호 정보
        "nick": nickname_receive,  # 닉네임 정보
        "Email": email_receive,  # email 정보
        "Address": address_receive,  # 주소 정보
        "phone": phone_receive,  # 휴대폰번호 정보
        "sex": sex_receive,  # 성별 정보
        "birth": birth_receive  # 생일 정보
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


# 운동내용 서버 저장
@app.route("/exer", methods=["POST"])
def exer_post():
    exer_receive = request.form['exer_give']
    id_receive = request.form['id_give']
    exer_list = list(db.exer.find({}, {'_id': False}))
    count = len(exer_list) + 1

    doc = {
        "id": id_receive,
        "num": count,
        "exer": exer_receive,
        "done": 0
    }

    db.exer.insert_one(doc)

    return jsonify({'msg': '저장 완료!'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"id": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/sign_up/check_dup_nick', methods=['POST'])
def check_dup_nick():
    nickname_receive = request.form['nickname_give']
    exists = bool(db.users.find_one({"nick": nickname_receive}))
    return jsonify({'result': 'success', 'exists': exists})


# my page 클릭시 data 불러오는 부분 #임시적인조치
@app.route("/mycontent", methods=["POST"])
def my_content():
    token_receive2 = request.cookies.get('mytoken')
    payload2 = jwt.decode(token_receive2, SECRET_KEY, algorithms=['HS256'])
    user_id_jwt = payload2["id"]  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

    my_content = list(db.indi.find({'id': user_id_jwt}, {'_id': False}))
    return jsonify({'my_content': my_content})


# 커뮤니티 클릭시 data 불러오는 부분
@app.route("/allcontent", methods=["POST"])
def all_content():
    all_content = list(db.indi.find({}, {'_id': False}))
    return jsonify({'all_content': all_content})

# input내용저장
@app.route("/save_content", methods=["POST"])
def save_content():
    token_receive2 = request.cookies.get('mytoken')
    text_receive = request.form['text_give']
    title_receive = request.form['title_give']
    payload2 = jwt.decode(token_receive2, SECRET_KEY, algorithms=['HS256'])
    user_id_jwt = payload2["id"]  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

    doc = {"text" : text_receive,"title" : title_receive,"id" : user_id_jwt ,'num': 0 }
    db.indi.insert_one(doc)

    return jsonify({'msg': '저장완료'})

#########################################################################################################


@app.route('/update_profile', methods=['POST'])
def save_img():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 프로필 업데이트
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/posting', methods=['POST'])
def posting():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 포스팅하기
        return jsonify({"result": "success", 'msg': '포스팅 성공'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route("/get_posts", methods=['GET'])
def get_posts():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 포스팅 목록 받아오기
        return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다."})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 좋아요 수 변경
        return jsonify({"result": "success", 'msg': 'updated'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
