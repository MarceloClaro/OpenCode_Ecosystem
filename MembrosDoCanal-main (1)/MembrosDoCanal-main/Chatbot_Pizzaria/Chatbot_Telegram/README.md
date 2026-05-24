Comando paa registro o bot no Telegram

curl -Method Post -Uri "https://api.telegram.org/bot<TOKEN do SEU BOT>/setWebhook" -Headers @{"Content-type"="application/json"} -Body '{"url": "<URL Vercel do seu BOT>/api/webhook"}'
