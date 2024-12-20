from flask import Flask, render_template, request, jsonify
import matplotlib.pyplot as plt
import ollama
import os
# import ollama
# import string

app = Flask(__name__)

# 학점 계산 함수
def calculate_gpa(grades):
    grade_points = {
        "A+": 4.5, "A": 4.0, "B+": 3.5, "B": 3.0,
        "C+": 2.5, "C": 2.0, "D+": 1.5, "D": 1.0, "F": 0.0
    }
    total_points = 0
    total_credits = 0

    for grade, credit in grades:
        total_points += grade_points.get(grade.upper(), 0) * credit
        total_credits += credit

    return total_points / total_credits if total_credits > 0 else 0.0

#응답
def your_response(satisfaction, myname, gpa, talktome):
    if satisfaction==["만족!/yes"]:
        response= ollama.generate(model='llama3', prompt=f"{myname} 이름을 가진 사람이 {gpa} 학점에 만족한다고 말했어. 한국어로 축하하는 대화를 해줘.'{talktome}'이 말에도 대화해줘")
    elif satisfaction==["조금은요/a_little_bit"]:
        response= ollama.generate(model='llama3', prompt=f"{myname} 이름을 가진 사람이 {gpa} 학점에 조금은 만족한다고 말했어. 한국어로 친구처럼 약간 위로와 축하하는 대화를 해줘.'{talktome}'이 말에도 대화해줘")
    elif satisfaction==["모르겠어요/i'm_not_sure"]:
        response= ollama.generate(model='llama3', prompt=f"{myname} 이름을 가진 사람이 {gpa} 학점에 대해 모르겠다고 말했어. 한국어로 친구처럼 격려의 대화를 해줘.'{talktome}'이 말에도 대화해줘")
    elif satisfaction==["딱히요/not_exactly"]:
        response= ollama.generate(model='llama3', prompt=f"{myname} 이름을 가진 사람이 {gpa} 학점에 딱히 만족하지 않는다고 말했어. 한국어로 해주싶은 대화를 해줘.'{talktome}'이 말에도 대화해줘")
    elif satisfaction==["아니요/no"]:
        response= ollama.generate(model='llama3', prompt=f"{myname} 이름을 가진 사람이 {gpa} 학점에 만족하지 않는다고 말했어. 한국어로 친구처럼 조언을 하는 대화를 해줘.'{talktome}'이 말에도 대화해줘.")
    else :
        response= ollama.generate(model='llama3', prompt=f"{myname} 이름을 가진 사람이 {gpa} 학점에 대해 슬프다 말했어. 한국어로 친구처럼 성심껏 위로하는 대화를 해줘.'{talktome}'이 말에도 대화해줘.")
    return response

def ollama_response(pri_message):
    response_message = pri_message.get('response', '응답을 생성할 수 없습니다.')
    return f"{response_message} \n 잘가요!"
    


# 메인 페이지
@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

# GPA 계산 API
@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.json
    grades = data.get("grades", [])

    # GPA 계산
    gpa = calculate_gpa(grades)

   # 성적 비율 계산
    grade_count = {grade: 0 for grade in ["A+", "A", "B+", "B", "C+", "C", "D+", "D", "F"]}
    for grade, _ in grades:
        grade_count[grade.upper()] += 1

    # 성적 비율 데이터 정리
    labels = [grade for grade, count in grade_count.items() if count > 0]
    sizes = [count for count in grade_count.values() if count > 0]

    # 파이 차트 생성
    plt.figure(figsize=(3,3))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors[:len(labels)])
    plt.title("Grade Distribution")

    # 이미지 저장
    chart_path = os.path.join("static", "chart.png")
    plt.savefig(chart_path)
    plt.close()

    return jsonify({"gpa": gpa, "chart_path": f"/{chart_path}"})

# 챗봇 응답 API
@app.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.json
    satisfaction = data.get("선택정보", "")
    myname = data.get("이름", "")
    talktome = data.get("말", "")
    gpa = data.get("gpa","")
    print(satisfaction)
    print(myname)
    pri_message = your_response(satisfaction, myname, gpa, talktome)
    response_message = ollama_response(pri_message)
    #response_message = ollama_response(satisfaction)
    return jsonify({"message": response_message})

if __name__ == '__main__':  
   app.run()