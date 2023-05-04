To access Postgres DB:

(dd_venv) abhay.bhadani:~/tttesst/duniyadekhegi_webproject$ sudo -u postgres psql
psql (9.5.24)
Type "help" for help.

postgres=# 

CREATE USER dd_user;
CREATE DATABASE duniyadekhegi_db;
GRANT ALL PRIVILEGES ON DATABASE duniyadekhegi_db TO dd_user;

postgres=# create user dd_user with encrypted password 'DuniyaDekhegi@321';

postgres=# alter user dd_user with encrypted password 'DuniyaDekhegi@321';

------------------------------------------------
To access Postgres Database

DATABASE_NAME:  duniyadekhegi_db
USER: dd_user
PASS: DuniyaDekhegi@321
(dd_venv) abhay.bhadani:~/tttesst/duniyadekhegi_webproject$ psql -h 0.0.0.0 -U dd_user -d duniyadekhegi_db -W


duniyadekhegi_db=>  \conninfo
You are connected to database "duniyadekhegi" as user "dd_user" on host "0.0.0.0" at port "5432".
SSL connection (protocol: TLSv1.2, cipher: ECDHE-RSA-AES256-GCM-SHA384, bits: 256, compression: off)
duniyadekhegi_db=> 


duniyadekhegi_db=> select inet_server_addr( ), inet_server_port( );
 inet_server_addr | inet_server_port 
------------------+------------------
 127.0.0.1        |             5432
(1 row)


-------------------------------------------

If postgres is running on Linux server, you can also use the following command

sudo netstat -plunt |grep postgres

tcp        0      0 127.0.0.1:5432          0.0.0.0:*               LISTEN      1644/postgres   


OR (if it comes as postmaster)

sudo netstat -plunt |grep postmaster


---------------------------------------------


(dd_venv) abhay.bhadani:~/tttesst/duniyadekhegi_webproject$ service postgresql status
● postgresql.service - PostgreSQL RDBMS
   Loaded: loaded (/lib/systemd/system/postgresql.service; enabled; vendor preset: enabled)
   Active: active (exited) since Wed 2020-12-02 09:10:08 IST; 8h ago
  Process: 2203 ExecStart=/bin/true (code=exited, status=0/SUCCESS)
 Main PID: 2203 (code=exited, status=0/SUCCESS)
    Tasks: 0
   Memory: 0B
      CPU: 0
   CGroup: /system.slice/postgresql.service

