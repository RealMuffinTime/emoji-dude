import datetime
import mariadb
import uuid
import secret_dev as secret

start_timestamp = None
db_connection = None


def get_start_timestamp():
    global start_timestamp
    if start_timestamp is None:
        start_timestamp = str(datetime.datetime.now().replace(microsecond=0))
    return start_timestamp


def get_curr_timestamp():
    return str(datetime.datetime.now().replace(microsecond=0))


def on_error(error_type, message):
    error_uuid = str(uuid.uuid4())
    log("error", error_type + " error uuid: " + error_uuid + ", " + message)
    return error_uuid


def log(status, message):
    try:
        status_prefix = None
        if status == "error":
            status_prefix = "[%s ERROR] "
        if status == "info":
            status_prefix = "[%s INFO ] "
        print(status_prefix % get_curr_timestamp() + message)
        log_file = open(r"log/%s_%s.txt" % (secret.secret, get_start_timestamp().replace(" ", "_").replace(":", "-")), "a", encoding="utf8")
        log_file.write(status_prefix % get_curr_timestamp() + message + "\n")
        log_file.close()
    except Exception as e:
        status_prefix = "[%s ERROR] " % get_curr_timestamp()
        print(status_prefix + "There is an error in a error reporter, HAHA, how ironic, %s" % str(e))


def get_db_connection():
    global db_connection
    if db_connection is None:
        try:
            db_connection = mariadb.connect(
                user=secret.database_user,
                password=secret.database_pass,
                host=secret.database_host,
                port=secret.database_port
            )
        except Exception as e:
            on_error("get_db_connection()", str(e).strip('.'))
    return db_connection


async def execute_sql(sql_term, fetch):
    try:
        cursor = get_db_connection().cursor(buffered=True)
        cursor.execute(f"USE `{secret.database_name}`")
        cursor.execute("SELECT * FROM stat_bot_online ORDER BY id DESC LIMIT 1")
        temp_fetch = cursor.fetchall()

        def restart():
            cursor.execute("INSERT INTO stat_bot_online (action) VALUES ('startup');")
            cursor.execute("INSERT INTO stat_bot_online (action) VALUES ('last seen');")

        if temp_fetch:
            if temp_fetch[0][1] == 'last seen' and (datetime.datetime.now() - temp_fetch[0][2]).seconds < 60:
                cursor.execute(
                    f"UPDATE stat_bot_online SET timestamp = '{datetime.datetime.now()}' WHERE id = '{temp_fetch[0][0]}';")
            else:
                restart()
        else:
            restart()

        cursor.execute(sql_term)
        get_db_connection().commit()
        if cursor.rowcount > 0 and fetch is True:
            return cursor.fetchall()
        if cursor.rowcount == 0 and fetch is True:
            return []
    except Exception as e:
        on_error("execute_sql()", str(e).strip('.'))
        return None
