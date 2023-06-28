FROM sahilgit55/mlrclone:latest

COPY . /app
WORKDIR /app
RUN chmod 777 /app

RUN pip3 install --no-cache-dir -r requirements.txt

RUN wget -O gclone https://7zmttn-my.sharepoint.com/personal/sahil66x_7zmttn_onmicrosoft_com/_layouts/15/download.aspx?share=EQ1g-0-cp5tLjr-i7CucsEQB_doR3jXKcA7kF0UXWF-oKw
RUN chmod +x gclone

CMD sh start.sh