from flask import Flask, render_template, request
import pandas as pd
import os
import requests

app = Flask(__name__)

# 🔹 設定 CSV 下載連結（對應不同班級）
CSV_URLS = {
    "901": "https://docs.google.com/spreadsheets/d/1ejmk2yRoyIEPuXTBC5J32ulLtk1exMkv/gviz/tq?tqx=out:csv&gid=395731245",
    "904": "https://docs.google.com/spreadsheets/d/1ejmk2yRoyIEPuXTBC5J32ulLtk1exMkv/gviz/tq?tqx=out:csv&gid=2067730854",
    "702": "https://docs.google.com/spreadsheets/d/1ejmk2yRoyIEPuXTBC5J32ulLtk1exMkv/gviz/tq?tqx=out:csv&gid=454504113",
    "901生活": "https://docs.google.com/spreadsheets/d/1ejmk2yRoyIEPuXTBC5J32ulLtk1exMkv/gviz/tq?tqx=out:csv&gid=2096141184",
    "904生活": "https://docs.google.com/spreadsheets/d/1ejmk2yRoyIEPuXTBC5J32ulLtk1exMkv/gviz/tq?tqx=out:csv&gid=775589910"
}

# 🔹 設定 CSV 存放資料夾
CSV_FOLDER = "grades"

# 🔹 確保 `grades/` 資料夾存在
if not os.path.exists(CSV_FOLDER):
    os.makedirs(CSV_FOLDER)

def download_csv(class_id):
    """ 下載最新的 CSV 檔案 """
    if class_id not in CSV_URLS:
        return False  # 若班級不存在，則不下載

    url = CSV_URLS[class_id]
    response = requests.get(url)

    if response.status_code == 200:
        csv_path = os.path.join(CSV_FOLDER, f"{class_id}.csv")
        with open(csv_path, "w", encoding="utf-8") as file:
            file.write(response.text)
        return True
    return False

@app.route('/')
def index():
    return render_template("query.html")  # 讓學生輸入學號、密碼、班級

@app.route('/query', methods=['POST'])
def query():
    student_id = request.form['student_id']  # 學生輸入學號
    password = request.form['password']  # 學生輸入密碼
    class_id = request.form['class_id']  # 學生輸入班級

    # 🔹 下載最新的 CSV
    success = download_csv(class_id)
    if not success:
        return f"<h2>❌ 無法下載 {class_id} 班的成績，請確認班級代碼是否正確！</h2><br><a href='/'>返回查詢</a>"

    # 🔹 讀取最新的 CSV
    csv_file = os.path.join(CSV_FOLDER, f"{class_id}.csv")
    df = pd.read_csv(csv_file, dtype=str).rename(columns=lambda x: x.strip().replace('"', ''))

    # 🔹 查詢該學生
    student_record = df[df["學號"] == student_id]

    if student_record.empty:
        return "<h2>❌ 查無此學生，請確認輸入是否正確！</h2><br><a href='/'>返回查詢</a>"

    # 🔹 驗證密碼
    correct_password = student_record.iloc[0]["密碼"]
    if correct_password != password:
        return "<h2>❌ 密碼錯誤，請重新輸入！</h2><br><a href='/'>返回查詢</a>"

    # 🔹 顯示成績（移除不必要的欄位）
    student_scores = student_record.drop(columns=["學號", "姓名", "密碼"])

    # 取得學生姓名和學號
    student_name = student_record.iloc[0]["姓名"]
    student_id = student_record.iloc[0]["學號"]

    # 讓表格顯示學生資訊
    student_info = f"<h2>📖 {student_name} ({student_id}) 的成績</h2>"

    # 顯示成績表
    return student_info + student_scores.to_html(index=False) + "<br><a href='/'>返回查詢</a>"
   
if __name__ == "__main__":  
    app.run(host="0.0.0.0", port=5050, debug=True)

