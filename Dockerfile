FROM python:3.9-slim

WORKDIR /ttmb

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "ttmb/main.py" ]
