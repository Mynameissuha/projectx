from flask import Flask
import redis
import os

app = Flask(__name__)

redis_url = os.getenv("REDIS_URL","redis://localhost:6379/0")
db_url = os.getenv("DB_URL")

redis_client = redis.Redis.from_url(redis_url)


def init_db():
    time.sleep(2)
    conn = psycopg2.connect(DB_URL)
    with conn.cursor() as cur:
        cur.execute("""
                    CREATE IF NOT EXISTS tokens (
                    token_id VARCHAR(50) PRIMARY KEY,
                    card_hash VARCHAR(64) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    """)
        conn.commit()
    conn.close()

init_db()

#генерация токена
@app.route("/api/v1/tokens/create",methods=["POST"])
def gen_token():
    data = request.json or {}
    card_number = data.get("card_number")
    client_id = data.get("client_id","anonymous")

    if not card_number or len(card_number) < 16:
        return jsonify({"error": "Неверный номер карты"}),400

    # защита от спама
    rate_limit_key = f"rate: {client_id}"
    requests_count = redis_client.incr(rate_limit_key)

    if requests_count == 1:
        redis_client.expire(rate_limit_key,10)

    if requests_count > 3:
        return jsonify({"error","Слишком много запросов! Защита от подбора карт"}) , 429

    generated_token = f"card_tok_{uuid.uuid4().hex[:12]}"
    card_hash = hashlib.sha256(card_number.encode()).hexdigest()

    try:
        conn = psycopg2.connect(DB_URL)
        with conn.cursor() as cur:
            cur.execute(
                    "INSERT INTO tokens (token_id, card_hash) VALUES (%s, %s)"
                    (generated_token,card_hash)
                    )
            conn.commit()
        conn.close()
    except Exception as e:
        return jsonify({"error": f"Ошибка базы данных: {str(e)}"}), 500

    return jsonify({
        "status": "SUCCESS",
        "client_id": client_id,
        "payment_token": generated_token,
        "info", "Реальный номер карты стерт из памяти устройства. Токен активен."
        })
if __name__ = "__main__":
    app.run(host= "0.0.0.0",port = 5000)
