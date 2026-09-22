# FROM docker.arvancloud.ir/python:3.12-alpine
FROM python:3.12-alpine

WORKDIR /usr/src/core

# Install dependencies
COPY ./requirements.txt .
# RUN apk add --no-cache gcc musl-dev libffi-dev \
#     && pip install --no-cache-dir --upgrade -r ./requirements.txt \
#     && apk del gcc musl-dev libffi-dev

RUN pip install -i https://mirror2.chabokan.net/pypi/simple/ --upgrade pip && pip install -r requirements.txt -i https://mirror2.chabokan.net/pypi/simple/


# Copy application files
COPY ./core .

# Set up an entrypoint script
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]