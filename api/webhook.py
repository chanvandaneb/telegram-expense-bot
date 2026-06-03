import os
import json
import logging
from datetime import datetime
import requests

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = "8859805024:AAFLeYGddC61-I5EDxZxZSoA4v-C7n33Q0M"
SHEET_ID = "1elx3vnJ2IlWaPYsOSnrRzQZDxFrCK7mVeT0CN2r_w7w"

# Categories
CATEGORIES = {
    "food": "🍔 Food",
    "transport": "🚕 Transport",
    "shopping": "🛍️ Shopping",
    "utilities": "💡 Utilities",
    "entertainment": "🎬 Entertainment",
    "health": "🏥 Health",
    "other": "📌 Other"
}

def send_message(chat_id, text):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Send error: {e}")
        return False

def parse_expense(text):
    """Parse expense from message"""
    parts = text.strip().split(maxsplit=2)
    
    if len(parts) < 3:
        return None
    
    try:
        amount = float(parts[0])
        category = parts[1].lower()
        description = parts[2]
        
        if category not in CATEGORIES:
            return None
        
        return {
            "amount": amount,
            "category": category,
            "description": description
        }
    except ValueError:
        return None

def handler(request):
    """Main Vercel serverless function"""
    try:
        # Only handle POST requests
        if request.method != 'POST':
            return {'statusCode': 200, 'body': 'ok'}
        
        # Parse request
        data = request.get_json()
        
        if "message" not in data:
            return {'statusCode': 200, 'body': 'ok'}
        
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        logger.info(f"Message from {chat_id}: {text}")
        
        # Handle commands
        if text == "/start":
            msg = "💰 Welcome to Expense Tracker!\n\nSend: <amount> <category> <description>\n\nExample: 50 food lunch\n\nCategories: food, transport, shopping, utilities, entertainment, health, other\n\nCommands: /today /month /summary /help"
            send_message(chat_id, msg)
        
        elif text == "/help":
            msg = "📋 Format: <amount> <category> <description>\n\nExamples:\n• 50 food lunch\n• 20 transport taxi\n• 100 shopping clothes"
            send_message(chat_id, msg)
        
        elif text == "/today":
            msg = "📊 Today's Summary\n\nFeature coming soon!\n\n(Google Sheets integration needed)"
            send_message(chat_id, msg)
        
        elif text == "/month":
            msg = "📊 This Month's Summary\n\nFeature coming soon!"
            send_message(chat_id, msg)
        
        elif text == "/summary":
            msg = "📈 Category Breakdown\n\nFeature coming soon!"
            send_message(chat_id, msg)
        
        else:
            # Try to parse as expense
            expense = parse_expense(text)
            
            if expense:
                msg = f"✅ Expense Logged!\n\n💵 ${expense['amount']:.2f}\n🏷️ {CATEGORIES[expense['category']]}\n📝 {expense['description']}"
                send_message(chat_id, msg)
                
                # TODO: Add to Google Sheet
                logger.info(f"Added: {expense}")
            else:
                msg = "❌ Invalid format!\n\nUse: 50 food lunch\nType /help"
                send_message(chat_id, msg)
        
        return {'statusCode': 200, 'body': 'ok'}
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return {'statusCode': 500, 'body': str(e)}
