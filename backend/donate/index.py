import json
import os
from typing import Dict, Any, Optional
import urllib.request
import urllib.parse
import pymysql

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Обрабатывает заявки на донат: отправляет уведомления в Telegram и обновляет базу SAMP при подтверждении оплаты
    '''
    method: str = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-Request-Id',
                'Access-Control-Max-Age': '86400'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    if method == 'POST':
        body_data = json.loads(event.get('body', '{}'))
        action = body_data.get('action')
        
        if action == 'create_request':
            return create_donate_request(body_data)
        elif action == 'confirm_payment':
            return confirm_payment(body_data)
        elif action == 'reject_payment':
            return reject_payment(body_data)
    
    return {
        'statusCode': 405,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'error': 'Method not allowed'}),
        'isBase64Encoded': False
    }


def create_donate_request(data: Dict[str, Any]) -> Dict[str, Any]:
    '''Создает заявку на донат и отправляет уведомление администратору'''
    nickname = data.get('nickname', '')
    amount = data.get('amount', 0)
    
    if not nickname or amount <= 0:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Invalid data'}),
            'isBase64Encoded': False
        }
    
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    admin_id = os.environ.get('TELEGRAM_ADMIN_ID')
    
    if not bot_token or not admin_id:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Bot not configured'}),
            'isBase64Encoded': False
        }
    
    request_id = f"{nickname}_{amount}_{int(data.get('timestamp', 0))}"
    
    message_text = f"🎮 Новая заявка на донат\n\n👤 Ник: {nickname}\n💰 Сумма: {amount} ₽\n🆔 ID заявки: {request_id}"
    
    keyboard = {
        'inline_keyboard': [[
            {'text': '✅ Оплатил', 'callback_data': f'confirm_{request_id}'},
            {'text': '❌ Не оплатил', 'callback_data': f'reject_{request_id}'}
        ]]
    }
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': admin_id,
        'text': message_text,
        'reply_markup': json.dumps(keyboard)
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as response:
            response.read()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': True, 'request_id': request_id}),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }


def confirm_payment(data: Dict[str, Any]) -> Dict[str, Any]:
    '''Подтверждает оплату и начисляет донат рубли в SAMP базу'''
    request_id = data.get('request_id', '')
    
    try:
        parts = request_id.split('_')
        nickname = parts[0]
        amount = int(parts[1])
        
        conn = pymysql.connect(
            host=os.environ.get('SAMP_DB_HOST'),
            user=os.environ.get('SAMP_DB_USER'),
            password=os.environ.get('SAMP_DB_PASSWORD'),
            database=os.environ.get('SAMP_DB_NAME'),
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with conn.cursor() as cursor:
            table = os.environ.get('SAMP_DB_TABLE')
            nickname_col = os.environ.get('SAMP_NICKNAME_COLUMN')
            donate_col = os.environ.get('SAMP_DONATE_COLUMN')
            
            sql = f"UPDATE {table} SET {donate_col} = {donate_col} + {amount} WHERE {nickname_col} = '{nickname}'"
            cursor.execute(sql)
            conn.commit()
        
        conn.close()
        
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        admin_id = os.environ.get('TELEGRAM_ADMIN_ID')
        
        message = f"✅ Оплата подтверждена!\n\n👤 Игрок: {nickname}\n💰 Начислено: {amount} донат рублей"
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': admin_id,
            'text': message
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': True}),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }


def reject_payment(data: Dict[str, Any]) -> Dict[str, Any]:
    '''Отклоняет заявку на оплату'''
    request_id = data.get('request_id', '')
    
    try:
        parts = request_id.split('_')
        nickname = parts[0]
        amount = int(parts[1])
        
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        admin_id = os.environ.get('TELEGRAM_ADMIN_ID')
        
        message = f"❌ Оплата отклонена\n\n👤 Игрок: {nickname}\n💰 Сумма: {amount} донат рублей"
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': admin_id,
            'text': message
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': True}),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }
