# Gebruik een lichte Python versie
FROM python:3.9-slim

# Werkmap in de container
WORKDIR /app

# Kopieer eerst requirements (voor slimmere caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopieer de rest van de code
COPY . .

# Poort openzetten (documentatie)
EXPOSE 5000

# Start de app
CMD ["python", "app.py"]
