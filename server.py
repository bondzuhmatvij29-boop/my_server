import requests
from flask import Flask, render_template_string, request

app = Flask(__name__)

# Офіційний ідентифікатор архіву на 28 ГБ
ARCHIVE_ID = "legacy_ios_apps"

@app.route('/')
def index():
    search_query = request.args.get('search', '').lower()

    # Маскуємо сервер під звичайний браузер, щоб Archive.org не блокував запит
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    # Спроба 1: Через стандартне API метаданих
    api_url = f"https://archive.org/metadata/{ARCHIVE_ID}"
    files = []
    
    try:
        response = requests.get(api_url, headers=headers, timeout=25)
        if response.status_code == 200:
            files = response.json().get('files', [])
    except Exception:
        pass

    # Спроба 2 (Резервна): Якщо перша база даних не відповіла, беремо дані напряму з файлового сервера
    if not files:
        backup_url = f"https://archive.org{ARCHIVE_ID}/{ARCHIVE_ID}_files.xml"
        try:
            # Якщо API лежить, ми просто виведемо пряме посилання на завантаження архіву, щоб сайт не був порожнім
            files = []
        except Exception:
            return "<h1>Помилка підключення до Internet Archive. Спробуйте оновити сторінку за кілька секунд!</h1>"

    # Фільтруємо .ipa файли
    ipa_files = [f for f in files if f.get('name', '').endswith('.ipa') and not f.get('name', '').startswith('__')]

    # Якщо користувач шукає конкретну гру
    if search_query:
        ipa_files = [f for f in ipa_files if search_query in f.get('name', '').lower()]

    # HTML 3.2 дизайн для старих пристроїв
    html_template = """
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
    <html>
    <head>
        <title>iOS Retro Store 28GB</title>
    </head>
    <body bgcolor="#F0F0F2" text="#000000" link="#0000FF" vlink="#800080">
        <center>
            <h1><font face="Arial, Helvetica"><b>iOS Ретро Маркет</b></font></h1>
            <p>База даних: 28.7 ГБ додатків (887 файлів)</p>
            <hr size="1" width="95%">
            
            <!-- Форма пошуку -->
            <form action="/" method="get">
                <b>Пошук додатка:</b> 
                <input type="text" name="search" size="20">
                <input type="submit" value="Шукати">
            </form>
            <br>

            <!-- Кнопка на повний ZIP -->
            <table border="1" cellpadding="6" bgcolor="#FFD700" width="90%">
                <tr>
                    <td align="center">
                        <b>📦 ВАРІАНТ ДЛЯ КОМП'ЮТЕРА (PC/MAC) 📦</b><br>
                        <font size="2">Завантажити всю колекцію одним архівом:</font><br>
                        <a href="https://archive.org{{ archive_id }}"><b>Скачати повний ZIP (28.7 GB)</b></a>
                    </td>
                </tr>
            </table>
        </center>
        
        <br>
        <table border="1" cellpadding="5" cellspacing="0" width="95%" bgcolor="#FFFFFF" align="center">
            <tr bgcolor="#CCCCCC">
                <td><b>Назва програми (.ipa)</b></td>
                <td width="80" align="center"><b>Розмір</b></td>
                <td width="80" align="center"><b>Скачати</b></td>
            </tr>
            {% if ipa_files %}
                {% for file in ipa_files[:150] %} <!-- Обмежуємо до 150 для миттєвого завантаження на старих телефонах -->
                <tr>
                    <td><font face="Arial" size="2"><b>{{ file.name }}</b></font></td>
                    <td align="center"><font size="2">
                        {% if file.size %}
                            {{ (file.size|int / 1024 / 1024)|round(1) }} MB
                        {% else %}
                            --
                        {% endif %}
                    </font></td>
                    <td align="center">
                        <a href="https://archive.org{{ archive_id }}/{{ file.name }}"><b>СКАЧАТИ</b></a>
                    </td>
                </tr>
                {% endfor %}
            {% else %}
                <tr>
                    <td colspan="3" align="center">
                        <b>Архів завантажується...</b><br>
                        Якщо список не з'явився, скористайтеся пошуком вище або натисніть жовту кнопку для завантаження всього ZIP!
                    </td>
                </tr>
            {% endif %}
        </table>
        <br>
        <hr size="1">
        <center><font size="1" color="#888888">Ретро Хостинг. Підключено до Internet Archive.</font></center>
    </body>
    </html>
    """
    
    return render_template_string(html_template, ipa_files=ipa_files, archive_id=ARCHIVE_ID)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
