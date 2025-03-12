# FOODGRAM

## Описание
Foodgram — это веб-приложение для публикации и поиска рецептов. Пользователи могут добавлять свои рецепты, сохранять понравившиеся в избранное, подписываться на авторов и формировать список покупок.

## Доступный функционал
+ Регаистрация и аутентификация пользователя
+ Публикация рецептов с изображениями
+ Добавление рецептов в избранное и их удаление из избранного
+ Подписка на авторов и отписка от них
+ Формирование списка покупок
+ Скачивание корзины текстовым файлом, при котором все ингредиенты формируются в один файл и суммируются
+ Фильтрация рецептов по тегам
+ Смена аватара
+ Смена пароля
+ Создание/удаление/редактирование собственных рецептов

##Технологии
+ Python
+ Django
+ Django REST Framework
+ Djoser
+ PostgreSQL
+ Docker, Docker compose
+ Gunicorn
+ Nginx
+ CI/CD (gitgub actions)

## Установка
### Как запустить проект:
1.Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:thefallenart/foodgram.git
```
```
cd foodgram
```
2.Cоздать и активировать виртуальное окружение:
```
python3 -m venv venv
```
```
# для OS Lunix и MacOS
source venv/bin/activate

# для OS Windows
source venv/Scripts/activate
```
3.Обновить pip:
```
python3 -m pip install --upgrade pip
```
4.Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
5. Создайте файл .env и заполните его данными
6.Запустите docker-compose в директории foodgram/infra
```
cd infra
docker-compose up
```
7.После сборки контейнеров выполните миграции в новом окне терминала
```
docker-compose exec backend python manage.py migrate
```
8.Создайте суперпользователя
```
docker-compose exec backend python manage.py createsuperuser
```
9.Загрузите статику 
```
docker-compose exec backend python manage.py collectstatic --no-input
```
10.Заполните базу данных ингредиентами
```
docker-compose exec backend python manage.py load_ingredients
Также потребуется создать теги в админ панеле для работы с рецептами
```
11.Проверка доступных эндпоинтов
```
http://localhost/
http://localhost/api/docs/
http://localhost/admin
```



