import asyncio
import datetime
import logging
import mariadb
import os
import shortuuid
import traceback


db_connection = None
start_timestamp = None
session_id = None


def get_start_timestamp(raw=False):
    global start_timestamp
    if start_timestamp is None:
        start_timestamp = datetime.datetime.now().replace(microsecond=0)
    if raw:
        return start_timestamp
    return str(start_timestamp)


def get_curr_timestamp(raw=False):
    if raw:
        return datetime.datetime.now()
    return str(datetime.datetime.now().replace(microsecond=0))


def error(name):
    trace = traceback.format_exc().rstrip("\n").split("\n")
    error_uuid = str(shortuuid.uuid())

    logging.error(name + ", " + error_uuid + ":")
    for message in trace:
        logging.error(message)

    return error_uuid


async def stat_bot_commands(command, status, user_id, guild_id):
    user_id = f"'{user_id}'" if user_id else "NULL"
    guild_id = f"'{guild_id}'" if guild_id else "NULL"
    await execute_sql(f"INSERT INTO stat_bot_commands (command, status, user_id, guild_id) VALUES ('{command}', '{status}', {user_id}, {guild_id})", False)


def get_db_connection():
    global db_connection
    if db_connection is None:
        try:
            db_connection = mariadb.connect(
                user=os.environ['BOT_DATABASE_USER'],
                password=os.environ['BOT_DATABASE_PASS'],
                host=os.environ['BOT_DATABASE_HOST'],
                port=int(os.environ['BOT_DATABASE_PORT'])
            )
            db_connection.auto_reconnect = True
        except Exception:
            error("get_db_connection()")
    return db_connection


async def execute_sql(sql_term, fetch, *args):
    try:
        cursor = get_db_connection().cursor(buffered=True)
        cursor.execute(f"USE `{os.environ['BOT_DATABASE_NAME']}`")
        if session_id is not None:
            cursor.execute(f"SELECT last_heartbeat FROM stat_bot_online WHERE id = '{session_id}'")
            last_heartbeat = cursor.fetchall()[0][0]

            if (get_curr_timestamp(True) - last_heartbeat).seconds >= 60:
                cursor.execute(f"UPDATE stat_bot_online SET last_heartbeat = '{get_curr_timestamp()}' WHERE id = '{session_id}'")

        if sql_term != "":
            cursor.execute(sql_term, [*args])
        get_db_connection().commit()
        if sql_term != "":
            if cursor.rowcount > 0 and fetch is True:
                return cursor.fetchall()
            if cursor.rowcount == 0 and fetch is True:
                return []
    except Exception:
        error(f"execute_sql()")
        logging.error(f"sql term: {sql_term}")
        logging.error(f"fetch: {fetch}")
        return []


async def startup():
    global session_id
    await execute_sql(f"INSERT INTO stat_bot_online (startup, last_heartbeat) VALUES ('{get_start_timestamp()}', '{get_curr_timestamp()}')", False)
    session_id = (await execute_sql("SELECT * FROM stat_bot_online ORDER BY id DESC LIMIT 1", True))[0][0]

if not os.path.exists("log"):
    os.makedirs("log")

asyncio.run(startup())
