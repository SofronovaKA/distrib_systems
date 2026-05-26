import time
import redis
from flask import Flask

app = Flask(__name__)

cache = redis.Redis(host='127.0.0.1', port=6379)

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/')
def hello():
    count = get_hit_count()
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                background-color: #d4edda;
                font-family: Arial, sans-serif;
                text-align: center;
                margin-top: 50px;
            }}
            h1 {{
                color: #155724;
            }}
            p {{
                font-size: 18px;
            }}
            strong {{
                font-size: 24px;
                color: #0066cc;
            }}
        </style>
    </head>
    <body>
        <h1 style="color:green">
            Бизнес-стенд "Инновации"
        </h1>
        <p>
            Посетителей сегодня:
            <strong>{}</strong>
        </p>
    </body>
    </html>
    '''.format(count)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
