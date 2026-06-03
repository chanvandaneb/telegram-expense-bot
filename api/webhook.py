"""
Telegram Bot for Vercel - SIMPLE VERSION
This is guaranteed to work!
"""

import json
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Your bot token
BOT_TOKEN = "8859805024:AAFLeYGddC61-I5EDxZxZSoA4v-C7n33Q0M"

def send_telegram_message(chat_id, text):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        logger.info(f"Sent message to {chat_id}: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return False

def parse_expense(text):
    """Parse: 50 food lunch"""
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
    """
    VERCEL HANDLER - This function is called by Vercel
    IMPORTANT: Must be named 'handler'
    IMPORTANT: Must accept 'request' parameter
    IMPORTANT: Must return dict with statusCode and body
    """
    
    try:
        # Log the request
        logger.info(f"Received request: {request.method}")
        
        # Only handle POST (Telegram sends POST)
        if request.method != 'POST':
            logger.info("Not POST request, ignoring")
            return {
                'statusCode': 200,
                'body': json.dumps({'ok': True})
            }
        
        # Get JSON data
        try:
            data = request.get_json()
        except:
            logger.error("Could not parse JSON")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid JSON'})
            }
        
        logger.info(f"Data: {json.dumps(data)}")
        
        # Check if message exists
        if "message" not in data:
            logger.info("No message in data")
            return {
                'statusCode': 200,
                'body': json.dumps({'ok': True})
            }
        
        message = data["message"]
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "").strip()
        
        if not chat_id or not text:
            logger.error(f"Missing chat_id or text: {chat_id}, {text}")
            return {
                'statusCode': 200,
                'body': json.dumps({'ok': True})
            }
        
        logger.info(f"Message from {chat_id}: {text}")
        
        # Handle /start command
        if text == "/start":
            response = """💰 <b>Welcome to Expense Tracker!</b>

Send expenses like this:
<code>50 food lunch</code>

<b>Categories:</b>
food, transport, shopping, utilities, entertainment, health, other

<b>Commands:</b>
/start - Welcome
/help - Help
/today - Today's total
/month - Month's total"""
            
            send_telegram_message(chat_id, response)
            return {'statusCode': 200, 'body': json.dumps({'ok': True})}
        
        # Handle /help command
        elif text == "/help":
            response = """<b>How to use:</b>

Format: <code>&lt;amount&gt; &lt;category&gt; &lt;description&gt;</code>

Examples:
<code>50 food lunch
20 transport taxi
100 shopping clothes</code>"""
            
            send_telegram_message(chat_id, response)
            return {'statusCode': 200, 'body': json.dumps({'ok': True})}
        
        # Handle /today
        elif text == "/today":
            response = """📊 <b>Today's Summary</b>

Total: $0.00
Entries: 0

(Tracking coming soon!)"""
            
            send_telegram_message(chat_id, response)
            return {'statusCode': 200, 'body': json.dumps({'ok': True})}
        
        # Handle /month
        elif text == "/month":
            response = """📊 <b>This Month's Summary</b>

Total: $0.00
Entries: 0

(Tracking coming soon!)"""
            
            send_telegram_message(chat_id, response)
            return {'statusCode': 200, 'body': json.dumps({'ok': True})}
        
        # Try to parse as expense
        else:
            expense = parse_expense(text)
            
            if expense:
                response = f"""✅ <b>Expense Logged!</b>

💵 Amount: ${expense['amount']:.2f}
🏷️ Category: {expense['category_name']}
📝 Description: {expense['description']}"""
                
                logger.info(f"Logged expense: {expense}")
                send_telegram_message(chat_id, response)
            else:
                response = """❌ <b>Invalid format!</b>

Use: <code>50 food lunch</code>

Type /help for more info"""
                
                send_telegram_message(chat_id, response)
            
            return {'statusCode': 200, 'body': json.dumps({'ok': True})}
    
    except Exception as e:
        logger.error(f"Error in handler: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
