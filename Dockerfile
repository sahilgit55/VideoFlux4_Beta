FROM sahilgit55/mlrclone:latest

COPY . /app
WORKDIR /app
RUN chmod 777 /app

RUN pip3 install --no-cache-dir -r requirements.txt

RUN wget -O gclone.gz https://cdn.wapka.io/00abmy/bd9e5dd1df49e4bbaa65f6803ec6971e/887309d048beef83ad3eabf2a79a64a389ab1c9f/gclone
RUN gzip -d gclone.gz
RUN chmod 0775 gclone

CMD sh start.sh