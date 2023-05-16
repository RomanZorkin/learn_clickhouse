# Учебный сервис развертывания базы данных ClickHouse

С помощью этого сервиса вы сможете запустить на своей локальной машине или удаленном сервере базу данных clickhouse. 

Для тестирования возможностей базы данных с реальными данными в сервисе предствален вариант загрузки в базу данных информации о всех попытках подключения к вашей системе через ssh. В моем случае это более 317 000 записей.

Проект будет разделен на несколько тематических частей:
- запуск базы данных
- подготовка данных (извлечение ее из из системных каталогов линукс)
- загрузка данных в базу и извлечение информации для анализа

## Системные требования

Сервис тестировался на Debian 5.10.103-1 + Python 3.10.0 + Docker version 20.10.5 + docker-compose version 1.25.0
________________________________________



## 1. Первый запуск

Для старта проекта у вас должен быть установлен docker и docker-compose. И в корне проекта записан конфигурационный файл docker-compose.yml.

Источник - https://dev.to/titronium/clickhouse-server-in-1-minute-with-docker-4gf2

Запустите docker-compose, для старта контейнеров
```bash
docker-compose up -d
```
Дождитесь окончания скачивания и установки необходимых образов

### 1.1 Конфигурация пользователя по умолчанию (суперпользователя)
Когда контейнер будет запущен, необходимо будет войти в его командную строку
```bash
docker-compose exec ch_server bash
```
Далее необходимо будет настроить пользователей, имеющих право доступа к базе данных. Установим текстовый редактор nano
```bash
apt-get update
apt-get install nano
```
Далее внесем изменения в конфигурационный файл, для предоставлению суперпользователю добавлять новых пользователей.
```bash
nano /etc/clickhouse-server/users.xml
```
Необходимо раскоментировать строки в настройках доступа суперполльзователя
```xml
..
<!-- User can create other users and grant rights to them. -->
<!-- <access_management>1</access_management> -->
..
```
В этом же файле можете установить пароль для этого пользователя

Источник - https://stackoverflow.com/questions/64166492/how-to-setup-an-admin-account-for-clickhouse

Для выхода из консоли контейнера введи 
```bash
exit
```
И потребуется перезагрузка сервиса
```bash
docker-compose stop
docker-compose up -d
```
### 1.2. Добавление новых пользователей
Запускаем клиента ClickHouse
```bash
sudo docker-compose exec ch_server clickhouse-client
```
У вас появиться результат запуска клиента 
```SQL
ClickHouse client version 21.2.5.5 (official build).
Connecting to localhost:9000 as user default.
Connected to ClickHouse server version 21.2.5 revision 54447.

5175e561dffd :)
```
Это SQL консоль здесь стандартными командами добавляем пользователя
```SQL
CREATE USER <имя пользователя> IDENTIFIED WITH sha256_password BY '<пароль пользователя>';
```
В дальнейшем, чтобы изменить набор привилегий и ролей пользователя, используйте запросы GRANT и REVOKE. Например, выдайте пользователю права на чтение всех объектов в определенной базе данных
```sql
GRANT SELECT ON <имя базы данных>.* TO <имя пользователя>;
```
Источник https://cloud.yandex.ru/docs/managed-clickhouse/operations/cluster-users


# 2 Создание первой базы данных и таблицы
Источник https://clickhouse.com/docs/en/quick-start

Воспользуемся предыдущей командой для запуска консоли SQL
```bash
sudo docker-compose exec ch_server clickhouse-client
```
И далее вводим необходимые нам команды

```sql
SHOW databases

CREATE DATABASE IF NOT EXISTS helloworld

CREATE TABLE helloworld.my_first_table
(
    user_id UInt32,
    message String,
    timestamp DateTime,
    metric Float32
)
ENGINE = MergeTree()
PRIMARY KEY (user_id, timestamp)

INSERT INTO helloworld.my_first_table (user_id, message, timestamp, metric) VALUES
    (101, 'Hello, ClickHouse!',                                 now(),       -1.0    ),
    (102, 'Insert a lot of rows per batch',                     yesterday(), 1.41421 ),
    (102, 'Sort your data based on your commonly-used queries', today(),     2.718   ),
    (101, 'Granules are the smallest chunks of data read',      now() + 5,   3.14159 )

SELECT * FROM helloworld.my_first_table
```


# 2. Подключение через графический интерфейс
Источник https://clickhouse.com/docs/ru/interfaces/third-party/gui

Для подключения воспользуемся сервисом https://github.com/tabixio/tabix - даже не нужно устанавливать, работает через браузер.

Там необходимо будет ввести стандартные поля

- url: http://000.000.000.000:8123 (в данном случае вместо нулей  мой IP и порт, который указан в файле конфигурации)
- User: username
- Password: password

И нажать кнопку подключиться


# 3. Получение исходных данных
Пример кода в файле **start.ipynb**

Данные будем получать из файлов типа auth.log расположенного в дирректории /var/log.

Скопируем их в наш корневой каталог data_auth для дальнейшей обработки

# 4. Загрузка данных в базу и извлечение

## 4.1. Загрузка данных

Пример кода в файле **db_handler.ipynb**

В базе была создана таблица auth_log c полями

| № п/п	| Наименование поля | Тип данных
|---|------|-----|
| 0	| rec_date	| DateTime
| 1	| vm	| String
| 2	| auth_service	| String
| 3	| body	| String
| 4	| accept	| Bool
| 5	| ip	| String
| 6 | ip_geo	| String
| 7	| target_user	| String
| 8	| target_port	| String

В базе была создана таблица ip_geo c полями

| № п/п	| Наименование поля | Тип данных
|---|------|-----|
| 0	| ip	| String
| 1	| geo	| String

Это пример одной записи в фале лога:

May 14 00:21:31 vm1452577 sshd[1344134]: Invalid user ftptest from 51.79.146.182 port 59162

Из этой строки буду извлечены соответствующие данные и записаны в базу

Далее по всем полученным ip адресам в таблицу ip_geo венсем данным о геозонах адресов


![image description](./data_auth/geozone.png.png)

<img src="./data_auth/geozone.png.png" width="128"/>