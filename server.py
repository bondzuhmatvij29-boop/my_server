import os
import time
import requests
from flask import Flask, render_template_string, request, Response

app = Flask(__name__)

# Основна колекція ретро-додатків
ARCHIVE_ID = "legacy_ios_apps"
ARCHIVE_API_URL = f"https://archive.org/metadata/{ARCHIVE_ID}"

# Глобальний кеш
CACHE_DATA = []
LAST_CACHE_TIME = 0
CACHE_TIMEOUT = 600  # Кеш на 10 хвилин


def get_cached_apps():
    global CACHE_DATA, LAST_CACHE_TIME
    current_time = time.time()

    # Віддаємо кеш, якщо він актуальний
    if CACHE_DATA and (current_time - LAST_CACHE_TIME < CACHE_TIMEOUT):
        return CACHE_DATA

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(ARCHIVE_API_URL, headers=headers, timeout=15)
        if response.status_code == 200:
            files = response.json().get('files', [])
            new_files = [
                f for f in files 
                if f.get('name', '').endswith('.ipa') and not f.get('name', '').startswith('__')
            ]
            if new_files:
                CACHE_DATA = new_files
                LAST_CACHE_TIME = current_time
    except Exception as e:
        print(f"Error fetching from archive.org: {e}")

    return CACHE_DATA


@app.route('/')
def index():
    search_query = request.args.get('search', '').lower()
    user_agent = request.headers.get('User-Agent', '').lower()

    # Визначаємо, чи це iOS-пристрій
    is_ios = any(device in user_agent for device in ['iphone', 'ipad', 'ipod'])

    files = get_cached_apps()

    # Фільтрація за пошуком
    if search_query:
        files = [f for f in files if search_query in f.get('name', '').lower()]

    html_template = """
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
    <html>
    <head>
        <title>iOS Retro Store 28GB</title>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body bgcolor="#F0F0F2" text="#000000" link="#0000FF" vlink="#800080">
        <center>
            <h1><font face="Arial, Helvetica"><b>iOS Магазин Приложений</b></font></h1>
            <p>База данных: 28.7 ГБ приложений</p>
            <hr size="1" width="95%">
            
            <form action="/" method="get">
                <b>Поиск приложения:</b> 
                <input type="text" name="search" size="20">
                <input type="submit" value="Искать">
            </form>
            <br>

            <table border="1" cellpadding="6" bgcolor="#FFD700" width="90%">
                <tr>
                    <td align="center">
                        <b>📦 ВАРИАНТ ДЛЯ КОМПЬЮТЕРА (PC/MAC) 📦</b><br>
                        <font size="2">Скачать всю коллекцию одним архивом:</font><br>
                        <a href="https://archive.org/download/{{ archive_id }}/{{ archive_id }}_archive.torrent"><b>Скачать полный архив (28.7 GB)</b></a>
                    </td>
                </tr>
            </table>
        </center>
        
        <br>
        <table border="1" cellpadding="5" cellspacing="0" width="95%" bgcolor="#FFFFFF" align="center">
            <tr bgcolor="#CCCCCC">
                <td><b>Название программы (.ipa)</b></td>
                <td width="80" align="center"><b>Размер</b></td>
                <td width="110" align="center"><b>Действие</b></td>
            </tr>
            {% if files %}
                {% for file in files[:150] %}
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
                        {% if is_ios %}
                            <a href="itms-services://?action=download-manifest&url={{ host_url }}plist/{{ file.name | urlencode }}"><b>Установить</b></a>
                        {% else %}
                            <a href="https://archive.org/download/{{ archive_id }}/{{ file.name }}" download><b>Скачать</b></a>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            {% else %}
                <tr>
                    <td colspan="3" align="center">
                        <b>Приложения не найдены или загружаются...</b><br>
                        Обновите страницу через пару секунд.
                    </td>
                </tr>
            {% endif %}
        </table>
        <br>
        <hr size="1">
        <center><font size="1" color="#888888">Ретро Хостинг. Подключено к Internet Archive.</font></center>
    </body>
    </html>
    """

    host_url = request.host_url.replace("http://", "https://")
    return render_template_string(
        html_template,
        files=files,
        archive_id=ARCHIVE_ID,
        host_url=host_url,
        is_ios=is_ios
    )


@app.route('/plist/<path:filename>')
def generate_plist(filename):
    """Генерація manifest.plist для iOS OTA-установки"""
    ipa_url = f"https://archive.org/download/{ARCHIVE_ID}/{filename}"
    app_title = filename.replace('.ipa', '')

    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>items</key>
    <array>
        <dict>
            <key>assets</key>
            <array>
                <dict>
                    <key>kind</key>
                    <string>software-package</string>
                    <key>url</key>
                    <string>{ipa_url}</string>
                </dict>
            </array>
            <key>metadata</key>
            <dict>
                <key>bundle-identifier</key>
                <string>com.retro.app.{app_title[:10].lower().replace(' ', '')}</string>
                <key>bundle-version</key>
                <string>1.0</string>
                <key>kind</key>
                <string>software</string>
                <key>title</key>
                <string>{app_title}</string>
            </dict>
        </dict>
    </array>
</dict>
</plist>"""

    return Response(plist_content, mimetype='text/xml')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
