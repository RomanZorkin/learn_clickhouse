# Учебный сервис развертывания базы данных ClickHouse

Для старта проекта у вас должен быть установлен docker и docker-compose. И записан конфигурационный файл docker-compose.yml в корне проекта.

Источник - https://dev.to/titronium/clickhouse-server-in-1-minute-with-docker-4gf2

## 1. Первый запуск

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