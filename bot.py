from fastapi import FastAPI, Request
import telebot
import os

TOKEN = os.getenv("7655460387:AAGS1lH2_U927NajVvGdxLrxcBAvFRzWDo0")  # Vercel'dagi env variables orqali
bot = telebot.TeleBot(TOKEN)

app = FastAPI()

@app.post("/")
async def webhook(request: Request):
    json_str = await request.body()
    update = telebot.types.Update.de_json(json_str.decode("utf-8"))
    bot.process_new_updates([update])
    return {"status": "ok"}

@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Salom! Vercel serveriga ulandi 🎉")
