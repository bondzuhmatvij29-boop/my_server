import os
import requests
from flask import Flask, render_template_string, request, Response, url_for

app = Flask(__name__)

ARCHIVE_ID = "legacy_ios_apps"

@app.route('/')
def index():
    search_query = request.args.get('search', '').lower()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    api_url = f"https://archive.org/metadata/{ARCHIVE_ID}"
    files = []
    
    try:
        response = requests.get(api_url, headers=headers, timeout=25)
        if response.status_code == 200:
            files = response.json().get('files', [])
    except Exception:
        pass

    ipa_files = [f for f in files if f.get('name', '').endswith('.ipa') and not f.get('name', '').startswith('__')]

    if search_query:
        ipa_files = [f for f in ipa_files if search_query in f.get('name', '').lower()]

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
            <p>База данных: 28.7 ГБ приложений (887 файлов)</p>
            <hr size="1" width="95%">
            
            <!-- Форма поиска -->
            <form action="/" method="get">
                <b>Поиск приложения:</b> 
                <input type="text" name="search" size="20">
                <input type="submit" value="Искать">
            </form>
            <br>

            <!-- Кнопка на полный ZIP -->
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
                <td width="100" align="center"><b>Действие</b></td>
            </tr>
            {% if ipa_files %}
                {% for file in ipa_files[:150] %}
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
                        <a href="itms-services://?action=download-manifest&url={{ host_url }}plist/{{ file.name | urlencode }}"><b>Установить</b></a>
                    </td>
                </tr>
                {% endfor %}
            {% else %}
                <tr>
                    <td colspan="3" align="center">
                        <b>Приложения не найдены или загружаются...</b><br>
                        Если список не появился, воспользуйтесь поиском выше.
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
    
    # Визначаємо HTTPS URL сервера
    host_url = request.host_url.replace("http://", "https://")
    return render_template_string(html_template, ipa_files=ipa_files, archive_id=ARCHIVE_ID, host_url=host_url)


@app.route('/plist/<path:filename>')
def generate_plist(filename):
    """Динамічна генерація manifest.plist для OTA установки на iOS"""
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
    
