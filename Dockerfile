FROM alpine

ENV VIRTUAL_ENV=/opt/venv
ENV DB_PATH=/db
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apk add --update --no-cache python3 py3-pip nodejs npm

WORKDIR /app

COPY scraper /app/scraper
RUN cd scraper && npm install && cd ..

COPY requirements.txt /app/requirements.txt
RUN python3 -m venv $VIRTUAL_ENV && pip3 install -r requirements.txt

COPY server /app/server
CMD ["uvicorn", "app:app", "--app-dir", "server", "--host", "0.0.0.0"]