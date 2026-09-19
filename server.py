import requests
from flask import Flask, render_template_string, request

app = Flask(__name__)

# Ідентифікатор архіву на 28 ГБ
ARCHIVE_ID = "legacy_ios_apps"

@app.route('/')
def index():
    # Отримуємо пошуковий запит, якщо користувач щось шукає
    search_query = request.args.get('search', '').lower()

    # 1. Запитуємо список файлів через API Інтернет-Архіву
    api_url = f"https://archive.org{ARCHIVE_ID}"
    try:
        response = requests.get(api_url, timeout=10).json()
        files = response.get('files', [])
    except Exception:
        return "<h1>Помилка підключення до бази даних архіву. Перевірте інтернет!</h1>"

    # 2. Фільтруємо лише .ipa файли
    ipa_files = [f for f in files if f['name'].endswith('.ipa')]

    # 3. Якщо є пошуковий запит, фільтруємо за назвою
    if search_query:
        ipa_files = [f for f in ipa_files if search_query in f['name'].lower()]

    # 4. Простий HTML 3.2 шаблон із рядком пошуку
    html_template = """
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
    <html>
    <head>
        <title>Мобільний Ретро Маркет</title>
    </head>
    <body bgcolor="#F5F5F7" text="#000000" link="#0000FF">
        <center>
            <h1>Ретро iOS Маркет</h1>
            <p>Сервер запущено прямо з Android через Pydroid 3!</p>
            <hr size="1" width="95%">
            
            <!-- Рядок пошуку додатка -->
            <form action="/" method="get">
                <b>Пошук гри:</b> 
                <input type="text" name="search" value="">
                <input type="submit" value="Знайти">
            </form>
            <br>

            <!-- Посилання на повний ZIP для комп'ютера -->
            <table border="1" cellpadding="8" bgcolor="#FFD700" width="90%">
                <tr>
                    <td align="center">
                        <b>📦 ВАРІАНТ ДЛЯ КОМП'ЮТЕРА 📦</b><br>
                        <a href="https://archive.org{{ archive_id }}"><b>Скачати весь архів ZIP (28.7 GB)</b></a>
                    </td>
                </tr>
            </table>
        </center>
        
        <br>
        <table border="1" cellpadding="5" cellspacing="0" width="95%" bgcolor="#FFFFFF" align="center">
            <tr bgcolor="#CCCCCC">
                <td><b>Назва програми (.ipa)</b></td>
                <td width="80" align="center"><b>Розмір</b></td>
                <td width="90" align="center"><b>Скачати</b></td>
            </tr>
            {% for file in ipa_files %}
            <tr>
                <td><b>{{ file.name }}</b></td>
                <td align="center"><font size="2">{{ (file.size|int / 1024 / 1024)|round(1) }} MB</font></td>
                <td align="center">
                    <a href="https://archive.org{{ archive_id }}/{{ file.name }}"><b>СКАЧАТИ</b></a>
                </td>
            </tr>
            {% endfor %}
        </table>
        <br>
        <hr size="1">
        <center><font size="1">Локальний сервер: Pydroid 3 (Android)</font></center>
    </body>
    </html>
    """
    
    return render_template_string(html_template, ipa_files=ipa_files, archive_id=ARCHIVE_ID)

if __name__ == '__main__':
    # host='0.0.0.0' дозволяє підключатися до сервера іншим пристроям у мережі Wi-Fi
    app.run(host='0.0.0.0', port=5000, debug=True)
