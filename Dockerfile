FROM python:3.11-alpine3.24

WORKDIR /app

COPY requirements.txt .
# Pull in available Alpine security updates before installing application
# packages. The pinned stable Alpine branch is supported through June 2028.
RUN apk upgrade --no-cache \
    && python -m pip install --no-cache-dir --upgrade \
        "setuptools==82.0.1" \
        "jaraco.context>=6.1.0" \
        "wheel>=0.46.2" \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
