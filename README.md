# FOODGRAM

## Описание
Foodgram — это веб-приложение для публикации и поиска рецептов. Пользователи могут добавлять свои рецепты, сохранять понравившиеся в избранное, подписываться на авторов и формировать список покупок.

##Доступный функционал
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

##Настройка CI/CD
1.Файл workflow уже готов 
2.Для адаптации его на своем сервере добавьте Secrets в GitHub Actions:

DOCKER_USERNAME                # имя пользователя в DockerHub
DOCKER_PASSWORD                # пароль пользователя в DockerHub
HOST                           # ip_address удалённого сервера
USER                           # логин на удалённом сервере
SSH_KEY                        # приватный ssh-ключ сервера
SSH_PASSPHRASE                 # Пароль для сервера
TELEGRAM_TO                    # ID аккаунта телеграм
TELEGRAM_TOKEN                 # Токен бота в телеграме на которого придет уведомление об успешном деплое 

##Запуск на сервере
1.Установите на сервере Docker и Docker Compose. Для запуска необходимо установить Docker и Docker Compose
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin
```
2.Проверьте, что Docker работает:
```
sudo systemctl status docker
```
3. Создайте на сервере директорию foodgram, в ней infra и в infra файл .env, после чего заполните его данными
```
POSTGRES_DB=kittygram
POSTGRES_USER=kittygram_user
POSTGRES_PASSWORD=kittygram_password
DB_NAME=kittygram
DB_HOST=db
DB_PORT=5432
SECRET_KEY=123
DEBUG=False
ALLOWED_HOSTS=127.0.0.1,localhost
```
4.Выполните команды:

git add .
git commit -m ""
git push
После этого будут запущены процессы workflow:
5.После успешного завершения процессов workflow на сервере выполним следующие команды:
Сделать миграции:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```
6.Собрать статические файлы для корректного отображения страниц
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --no-input
```
7.Создать суперюзера:
```
sudo docker compose -f docker-compose.production.yml exec -it backend python manage.py createsuperuser
```
8.Загрузить в БД информацию об ингредиентах:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py load_ingredients
```
9. Создать теги через админ панель для корректрой работы с рецептами

##Примеры запросов: 
1. Регистрация пользователя
```
POST /api/users/
Запрос:
{
  "email": "user@example.com",
  "username": "new_user",
  "first_name": "John",
  "last_name": "Doe",
  "password": "securepassword123"
}
```
2.Добавление рецепта в избранное
```
POST /api/recipes/{id}/favorite/
{
  "id": 1,
  "name": "Омлет",
  "image": "http://example.com/media/recipes/omelet.jpg",
  "cooking_time": 10
}
```
3.Подписка на пользователя
```
POST /api/users/{id}/subscribe/
{
  "email": "author@example.com",
  "id": 2,
  "username": "author_user",
  "first_name": "Jane",
  "last_name": "Doe",
  "is_subscribed": true,
  "recipes": [
    {
      "id": 2,
      "name": "Блины",
      "image": "http://example.com/media/recipes/pancakes.jpg",
      "cooking_time": 20
    }
  ],
  "recipes_count": 1
}
```
##Автор
Кирилл - TheFallenArt

