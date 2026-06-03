import json
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8859805024:AAFLeYGddC61-I5EDxZxZSoA4v-C7n33Q0M"

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        response = requests.post(url, json=data, timeout=10)
        logger.info(f"Sent: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error: {e}")
        return False

def parse_expense(text):
    try:
        parts = text.strip().split(maxsplit=2)
        if len(parts) < 3:
            return None
        amount = float(parts[0])
        category = parts[1].lower()
        description = parts[2]
        categories = {
            "food": "🍔 Food",
            "transport": "🚕 Transport",
            "shopping": "🛍️ Shopping",
            "utilities": "💡 Utilities",
            "entertainment": "🎬 Entertainment",
            "health": "🏥 Health",
            "other": "📌 Other"
        }
        if category not in categories:
            return None
        return {
            "amount": amount,
            "category": category,
            "category_name": categories[category],
            "description": description
        }
    except:
        return None

def handler(request):
    try:
        logger.info(f"Request: {request.method}")
        if request.method != 'POST':
            return {'statusCode': 200, 'body': json.dumps({'ok': True})}
        try:
            data = request.get_json()
        except:
            logger.error("Invalid JSON")
            return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid JSON'})}
        logger.info(f"Data: {json.dumps(data)}")
        if "message" not in data:
            logger.info("No message")
            return {'statusCode': 200, 'body': json.dumps({'ok': True})}
        message = data["message"]
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "").strip()
        if not chat_id or not text:
            logger.error(f"Missing: {chat_id}, {text}")
            return {'statusCode': 200, 'body': json.dumps({'ok': True})}
        logger.info(f"Message: {text}")
        if text == "/start":
            response = """💰 <b>Welcome to Expense Tracker!</b>

Send: <code>50 food lunch</code>

<b>Categories:</b>
food, transport, shopping, utilities, entertainment, health, other

<b>Commands:</b>
/help - Help
/today - Today's total
/month - Month's total"""
            send_telegram_message(chat_id, response)
            return {'statusCode': 200, 'body': json.dumps({'ok': True})}
        elif text == "/help":
            response = """<b>Format:</b> <code>&lt;amount&gt; &lt;category&gt; &lt;description&gt;</code>

<b>Examples:</b>
<code>50 food lunch
20 transport taxi
100 shopping clothes</code>"""
            send_telegram_message(chat_id, response)
            return {'statusCode': 200, 'body': json.dumps({'ok': True})}
        elif text == "/today":
            response = """📊 <b>Today's Summary</b>

Total: $0.00
Entries: 0"""
            send_telegram_message(chat_id, response)
            return {'statusCode': 200, 'body': json.dumps({'ok': True})}
        elif text == "/month":
            response = """📊 <b>This Month's Summary</b>

Total: $0.00
Entries: 0"""
            send_telegram_message(chat_id, response)
            return {'statusCode': 200, 'body': json.dumps({'ok': True})}
        else:
            expense = parse_expense(text)
            if expense:
                response = f"""✅ <b>Expense Logged!</b>

💵 ${expense['amount']:.2f}
🏷️ {expense['category_name']}
📝 {expense['description']}"""
                logger.info(f"Logged: {expense}")
                send_telegram_message(chat_id, response)
            else:
                response = """❌ <b>Invalid format!</b>

Use: <code>50 food lunch</code>
Type /help"""
                send_telegram_message(chat_id, response)
            return {'statusCode': 200, 'body': json.dumps({'ok': True})}
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
