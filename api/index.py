from flask import Flask, render_template, request, redirect, url_for, session
import csv
import os
import re

app = Flask(__name__)
app.secret_key = "dlrjsduwnstoddlfdmfdnlgksdnpqtkdslxm"  # 세션 암호화를 위한 키
app.config["SESSION_PERMANENT"] = False

session_initialized = False 

# In-memory storage for rolling paper messages
messages = []

PASSWORD = {20243262, 20241962, 20241965, 20243272, 20241989, 20243264, 20243283, 20241971, 20241972, 20241974, 20241978, 20241984, 20243282, 20241982}

@app.before_request
def clear_session_on_restart():
    global session_initialized
    if not session_initialized:
        session.clear()  # 모든 세션 데이터 초기화
        session_initialized = True  # 한 번 실행 후 다시 실행되지 않게 함
        print("🔄 서버 재시작됨: 세션 초기화 완료")

@app.route('/')
def main():
    return render_template('main.html', authenticated=session.get("authenticated", False))


@app.route("/gallery")
def gallery():
    if not session.get("authenticated"):  # 인증되지 않았으면 인증 페이지로 리디렉트
        return redirect(url_for("authentication"))
    image_folder = "static/images/gallery"
    image_files = [img for img in os.listdir(image_folder) if img.endswith((".jpg", ".png", ".jpeg"))]
    
    image_files = sorted(image_files, key=lambda x: int(os.path.splitext(x)[0]))

    photos = [{"src": f"/{image_folder}/{img}"} for img in image_files]

    return render_template("gallery.html", photos=photos)

def load_messages():
    messages = []
    with open("static/roll.csv", "r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            messages.append(row)  # {'이름': '홍길동', '내용': '생일 축하해!'}

    # 한글 이름이 먼저 오고, 특수문자가 포함된 이름은 뒤로 정렬
    messages = sorted(messages, key=lambda x: (not bool(re.match(r"^[가-힣]", x["이름"])), x["이름"].strip()))

    return messages

@app.route("/rolling_paper")
def rolling_paper():
    messages = load_messages()  # CSV 데이터 가져오기
    return render_template("rolling_paper.html", messages=messages)

# 인증 페이지 (로그인)
@app.route("/authentication", methods=["GET", "POST"])
def authentication():
    if request.method == "POST":
        entered_password = request.form.get("password")
        next_page = request.form.get("next", "/")  # 기본값: 메인 페이지
        try:
            entered_password = int(entered_password)
        except ValueError:
            return render_template("authentication.html", error="숫자만 입력하세요!", next=next_page)

        if entered_password in PASSWORD:
            session["authenticated"] = True  # 로그인 성공
            return redirect(next_page)  # 로그인 후 next_page로 이동
        else:
            return render_template("authentication.html", error="비밀번호가 틀렸습니다!", next=next_page)
    return render_template("authentication.html", next=request.args.get("next", "/"))


# 로그아웃
@app.route('/logout')
def logout():
    session.pop('authenticated', None)  # 로그아웃 시 세션에서 상태 제거
    return render_template("main.html")

# if __name__ == '__main__':
#     app.run(debug=True)