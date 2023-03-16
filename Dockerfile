# Создать образ на основе базового слоя python (там будет ОС и интерпретатор Python).
# 3.10 — используемая версия Python.
# slim — обозначение того, что образ имеет только необходимые компоненты для запуска,
# он не будет занимать много места при развёртывании.
FROM python:3.10.6-slim

# Запустить команду создания директории внутри контейнера
RUN mkdir /tg_bot

# Скопировать с локального компьютера файл зависимостей
# в директорию /tg_bot.
COPY ./requirements.txt /tg_bot

RUN pip install -U pip
# Выполнить установку зависимостей внутри контейнера.
RUN pip install -r /tg_bot/requirements.txt --no-cache-dir

# Скопировать содержимое директории c локального компьютера
# в директорию /tg_bot.
COPY . /tg_bot

# Сделать директорию /tg_bot рабочей директорией.
WORKDIR /tg_bot