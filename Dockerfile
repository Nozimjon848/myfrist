# Python 3.10 imidjidan foydalanamiz
FROM python:3.10

# Ishchi direktoriyani o'rnatamiz
WORKDIR /app

# Kerakli fayllarni konteynerga ko'chiramiz
COPY . /app

# Kerakli kutubxonalarni o'rnatamiz
RUN pip install --no-cache-dir -r requirements.txt

# Botni ishga tushirish
CMD ["python", "bot.py"]
