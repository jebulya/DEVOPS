import logging
import re
import paramiko
import os
from dotenv import load_dotenv

import psycopg2
from psycopg2 import Error

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

load_dotenv()
TOKEN = os.getenv('TOKEN')

SECRET_KEY = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(
        f'Добрый день, {user.full_name}\!\nЧтобы войти в раздел *Мониторинга системы*, воспользуйтесь командой /monitoring\.\nКоманда /findPhoneNumbers \- поиск телефонных номеров\;\nКоманда /findEmails \- поиск адресов электронной почты\;\n/verifyPassword \- проверка пароля на сложность;\n/get\_emails \- прочитать адреса из базы данных\;\n/get\_phone\_numbers \- прочитать номера телефонов из базы данных\;\nВажно\! По умолчанию базы данных пусты\.', parse_mode='MarkdownV2')
    

def helpCommand(update: Update, context):
    update.message.reply_text('Help!')

def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'findPhoneNumbers'

def findEmailsCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска email: ')
    return 'findEmails'

def verifyPasswordCommand(update: Update, context):
    update.message.reply_text('Введите пароль')

    return 'verifyPassword'

def get_releaseCommand(update: Update, context):
    return 'get_release'


def get_unameCommand(update: Update, context):
    return 'get_uname'


def get_uptimeCommand(update: Update, context):
    return 'get_uptime'


def get_dfCommand(update: Update, context):
    return 'get_df'


def get_mpstatCommand(update: Update, context):
    return 'get_mpstat'


def get_wCommand(update: Update, context):
    return 'get_w'


def get_authsCommand(update: Update, context):
    return 'get_auths'


def get_criticalCommand(update: Update, context):
    return 'get_critical'


def get_psCommand(update: Update, context):
    return 'get_release'


def get_ssCommand(update: Update, context):
    return 'get_ss'


def get_apt_listCommand(update: Update, context):
    update.message.reply_text(
        'Введите "Все", чтобы вывести все установленные пакеты (доступно 10)\nВведите название определённого пакета, чтобы найти информацию по нему')
    return 'get_apt_list'


def get_services_listCommand(update: Update, context):
    return 'get_services'


def monitoring(update: Update, context):
    update.message.reply_text('Вы вошли в раздел *Мониторинга* системы\.', parse_mode='MarkdownV2')
    update.message.reply_text('Команда /get_release - информация о релизе')
    update.message.reply_text(
        'Команда /get_uname - информация о архитектуре процессора, имени хоста системы и версии ядра.')
    update.message.reply_text('Команда /get_uptime - информация о времени работы')
    update.message.reply_text('Команда /get_df - сбор информации о состоянии оперативной памяти.')
    update.message.reply_text('Команда /get_mpstat - информация о о производительности системы')
    update.message.reply_text('Команда /get_w - информация о работающих в данной системе пользователях.')
    update.message.reply_text('Команда /get_auths - последние 10 входов в систему')
    update.message.reply_text('Команда /get_critical - последние 5 критических события')
    update.message.reply_text('Команда /get_ps - информация о запущенных процессах')
    update.message.reply_text('Команда /get_ss - информация об используемых портах')
    update.message.reply_text('Команда /get_apt_list - информация об установленных пакетах')
    update.message.reply_text('Команда /get_services - информация о запущенных сервисах')


def connect(update: Update, context, input_command):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    userkali = os.getenv('RM_USER')
    passkali = os.getenv('RM_PASSWORD')

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(hostname=host, username=userkali, password=passkali, port=port)
    stdin, stdout, stderr = client.exec_command(input_command)
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END


def get_release(update: Update, context):
    command = 'lsb_release -a'
    connect(update, context, command)


def get_uname(update: Update, context):
    command = 'uname -a'
    connect(update, context, command)


def get_uptime(update: Update, context):
    command = 'uptime'
    connect(update, context, command)


def get_df(update: Update, context):
    command = 'df -h'
    connect(update, context, command)


def get_mpstat(update: Update, context):
    command = 'mpstat'
    connect(update, context, command)


def get_w(update: Update, context):
    command = 'w'
    connect(update, context, command)


def get_auths(update: Update, context):
    command = 'last -n 10'
    connect(update, context, command)


def get_critical(update: Update, context):
    command = 'journalctl -p err -n 5'
    connect(update, context, command)


def get_ps(update: Update, context):
    command = 'ps | head -n 20'
    connect(update, context, command)


def get_apt_list(update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    userkali = os.getenv('RM_USER')
    passkali = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=userkali, password=passkali, port=port)
    user_input = update.message.text.lower()

    if user_input == 'все' or user_input == 'Все':
        stdin, stdout, stderr = client.exec_command('dpkg -l | grep "^ii" | head -n 15')
        data = stdout.read() + stderr.read()
        client.close()
        data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
        update.message.reply_text(data)
        return ConversationHandler.END
    else:
        # update.message.reply_text('Введите название пакета для получения информации')
        user_input = update.message.text
        stdin, stdout, stderr = client.exec_command(f'dpkg -s {user_input} | head -n 20')
        data = stdout.read() + stderr.read()
        client.close()
        update.message.reply_text(data.decode())
        return ConversationHandler.END


def get_ss(update: Update, context):
    command = 'ss | head -n 20'
    connect(update, context, command)


def get_services(update: Update, context):
    command = 'systemctl list-units --type=service --state=running | head -n 20'
    connect(update, context, command)


def findPhoneNumbers(update: Update, context):
    user_input = update.message.text  # Получаем текст, содержащий(или нет) номера телефонов

    phoneNumRegex = re.compile(
        r'(?:\+7|8)(?: \(\d{3}\) \d{3}-\d{2}-\d{2}|\d{10}|\(\d{3}\)\d{7}| \d{3} \d{3} \d{2} \d{2}| \(\d{3}\) \d{3} \d{2} \d{2}|-\d{3}-\d{3}-\d{2}-\d{2})')  # формат 8 (000) 000-00-00

    phoneNumberList = phoneNumRegex.findall(user_input)  # Ищем номера телефонов

    if not phoneNumberList:  # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return  # Завершаем выполнение функции

    phoneNumbers = ''  # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i + 1}. {phoneNumberList[i]}\n'  # Записываем очередной номер

    update.message.reply_text(phoneNumbers)  # Отправляем сообщение пользователю

    update.message.reply_text('Хотите ли вы сохранить это в базу данных? Введите "да"')

    context.user_data['phone_numbers'] = phoneNumberList
    return "writePhoneNumbers"

def writePhoneNumbers(update: Update, context):
    user_input2 = update.message.text.lower()
    phone_numbers = context.user_data.get('phone_numbers')
    if user_input2 == 'да':
        host_db = os.getenv('DB_HOST')
        port_db = os.getenv('DB_PORT')
        username_db = os.getenv('DB_USER')
        password_db = os.getenv('DB_PASSWORD')
        database_db = os.getenv('DB_DATABASE')
        connection = None
        # print(username_db, password_db, database_db, host_db, port_db)
        try:
            connection = psycopg2.connect(user=username_db,
                                          password=password_db,
                                          host=host_db,
                                          port=port_db,
                                          database=database_db)

            cursor = connection.cursor()
            for number in phone_numbers:
                cursor.execute("INSERT INTO phone_numbers(phone_number) VALUES (%s);", (number,))
            connection.commit()
            update.message.reply_text('Данные сохранены. Используйте команду /get_phone_numbers, чтобы посмотреть')
            logging.info("Команда успешно выполнена")
        except (Exception, Error) as error:
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
            update.message.reply_text('Данные не сохранены. Произошла ошибка')
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
                logging.info("Соединение с PostgreSQL закрыто")
    else:
        update.message.reply_text('Данные не сохранены')
        return ConversationHandler.END

    return ConversationHandler.END  # Завершаем работу обработчика диалога

def findEmails(update: Update, context):
    user_input = update.message.text

    emailRegex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')

    email_list = emailRegex.findall(user_input)

    if not email_list:
        update.message.reply_text('Адреса почты не найдены')
        return

    emails = ''
    for i in range(len(email_list)):
        emails += f'{i + 1}. {email_list[i]}\n'

    update.message.reply_text(emails)
    update.message.reply_text('Хотите ли вы сохранить это в базу данных? Введите "да"')

    context.user_data['emails'] = email_list
    return "writeEmails"

def writeEmails(update: Update, context):
    user_input2 = update.message.text.lower()
    emails = context.user_data.get('emails')
    if user_input2 == 'да':
        host_db = os.getenv('DB_HOST')
        port_db = os.getenv('DB_PORT')
        username_db = os.getenv('DB_USER')
        password_db = os.getenv('DB_PASSWORD')
        database_db = os.getenv('DB_DATABASE')
        connection = None
        # print(username_db, password_db, database_db, host_db, port_db)
        try:
            connection = psycopg2.connect(user=username_db,
                                          password=password_db,
                                          host=host_db,
                                          port=port_db,
                                          database=database_db)

            cursor = connection.cursor()
            for email in emails:
                cursor.execute("INSERT INTO emails(email) VALUES (%s);", (email,))
            connection.commit()
            logging.info("Команда успешно выполнена")
        except (Exception, Error) as error:
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
            update.message.reply_text('Данные не сохранены. Произошла ошибка')
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
                update.message.reply_text('Данные сохранены. Используйте команду /get_emails, чтобы посмотреть')
                logging.info("Соединение с PostgreSQL закрыто")
    else:
        update.message.reply_text('Данные не сохранены')
        return ConversationHandler.END

    return ConversationHandler.END  # Завершаем работу обработчика диалога


def verifyPassword(update: Update, context):
    user_input = update.message.text
    password_regex = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()_\-])[A-Za-z\d!@#$%^&*()_\-]{8,}$')

    if password_regex.match(user_input):
        update.message.reply_text("Пароль сложный.")
    else:
        update.message.reply_text("Пароль простой.")
    return ConversationHandler.END


def get_repl_logsCommand(update: Update, context):
    return 'get_repl_logs'


def get_repl_logs(update: Update, context):
    logs_dir = '/var/log/postgresql/'   
    result = ''

    try:
        logger.info(f"Reading log files from directory: {logs_dir}")
        for filename in os.listdir(logs_dir):
            if filename.endswith('.log'):
                logger.info(f"Found log file: {filename}")
                with open(os.path.join(logs_dir, filename), 'r') as file:
                    for line in file:
                        if "repl" in line:
                            result+= line
        logger.debug(f"Log reading successful. Result length: {len(result)}")
        update.message.reply_text(result[-1500:])
    except Exception as e:
        logger.error(f"Error reading log files: {e}")
        update.message.reply_text("Произошла ошибка при чтении логов.")

def echo(update: Update, context):
    update.message.reply_text(update.message.text)


def get_emails(update: Update, context):
    host_db = os.getenv('DB_HOST')
    port_db = os.getenv('DB_PORT')
    username_db = os.getenv('DB_USER')
    password_db = os.getenv('DB_PASSWORD')
    database_db = os.getenv('DB_DATABASE')
    connection = None
    # print(username_db, password_db, database_db, host_db, port_db)
    try:
        connection = psycopg2.connect(user=username_db,
                                      password=password_db,
                                      host=host_db,
                                      port=port_db,
                                      database=database_db)

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM emails")
        data = cursor.fetchall()
        output = ""
        for row in data:
            output += "id: " + str(row[0]) + " email: " + str(row[1]) + "\n"
        update.message.reply_text(output)
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
        update.message.reply_text('Не удалось получить данные. Произошла ошибка')
    finally:
        if connection is not None:
            cursor.close()
            connection.close()

def get_phone_numbers(update: Update, context):
    host_db = os.getenv('DB_HOST')
    port_db = os.getenv('DB_PORT')
    username_db = os.getenv('DB_USER')
    password_db = os.getenv('DB_PASSWORD')
    database_db = os.getenv('DB_DATABASE')
    connection = None
    # print(username_db, password_db, database_db, host_db, port_db)
    try:
        connection = psycopg2.connect(user=username_db,
                                      password=password_db,
                                      host=host_db,
                                      port=port_db,
                                      database=database_db)

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM phone_numbers")
        data = cursor.fetchall()
        output = ""
        for row in data:
            output += "id: " + str(row[0]) + " phone number: " + str(row[1]) + "\n"
        update.message.reply_text(output)
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
        update.message.reply_text('Не удалось получить данные. Произошла ошибка')
    finally:
        if connection is not None:
            cursor.close()
            connection.close()


def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('findPhoneNumbers', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'writePhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, writePhoneNumbers)]
        },
        fallbacks=[]
    )
    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('findEmails', findEmailsCommand)],
        states={
            'findEmails': [MessageHandler(Filters.text & ~Filters.command, findEmails)],
            'writeEmails': [MessageHandler(Filters.text & ~Filters.command, writeEmails)],
        },
        fallbacks=[]
    )

    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verifyPassword', verifyPasswordCommand)],
        states={
            'verifyPassword': [MessageHandler(Filters.text & ~Filters.command, verifyPassword)],
        },
        fallbacks=[]
    )
    convHandlerGetAptList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_listCommand)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )

    # Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerVerifyPassword)
    dp.add_handler(convHandlerGetAptList)
    dp.add_handler(CommandHandler("monitoring", monitoring))
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    # dp.add_handler(CommandHandler("get_apt_list", get_apt_list))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_services", get_services))
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))

    # Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
