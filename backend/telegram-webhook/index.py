import json
import os
from typing import Dict, Any
import urllib.request

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Обрабатывает webhook от Telegram бота для кнопок подтверждения/отклонения оплаты
    '''
    method: str = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '86400'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    if method == 'POST':
        body_data = json.loads(event.get('body', '{}'))
        
        if 'callback_query' in body_data:
            callback = body_data['callback_query']
            callback_data = callback.get('data', '')
            callback_id = callback.get('id')
            
            bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
            
            if callback_data.startswith('confirm_'):
                request_id = callback_data.replace('confirm_', '')
                
                url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"
                payload = {
                    'callback_query_id': callback_id,
                    'text': '✅ Оплата подтверждена! Донат рубли начислены.'
                }
                
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode('utf-8'),
                    headers={'Content-Type': 'application/json'}
                )
                urllib.request.urlopen(req)
                
            elif callback_data.startswith('reject_'):
                request_id = callback_data.replace('reject_', '')
                
                url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"
                payload = {
                    'callback_query_id': callback_id,
                    'text': '❌ Оплата отклонена'
                }
                
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode('utf-8'),
                    headers={'Content-Type': 'application/json'}
                )
                urllib.request.urlopen(req)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'ok': True}),
            'isBase64Encoded': False
        }
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'ok': True}),
        'isBase64Encoded': False
    }
