import logging
import re
import paramiko
import os
from dotenv import load_dotenv

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

TOKEN = "6924289771:AAEn_7dDJ5cQK1hwz1B6rV2Toc3KkMHLHzM"

load_dotenv()
SECRET_KEY= os.getenv('SECRET_KEY')
DATABASE_URL= os.getenv('DATABASE_URL')
host = os.getenv('HOST')
port = os.getenv('PORT')
userkali = os.getenv('USER')
passkali = os.getenv('PASSWORD')

logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Добрый день, {user.full_name}\!\nЧтобы войти в раздел *Мониторинга системы*, воспользуйтесь командой /monitoring\.\nКоманда /findPhoneNumbers \- поиск телефонных номеров\;\nКоманда /findEmails \- поиск адресов электронной почты\;\n/verifyPassword \- проверка пароля на сложность', parse_mode='MarkdownV2')


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
    update.message.reply_text('Введите "Все", чтобы вывести все установленные пакеты (доступно 10)\nВведите название определённого пакета, чтобы найти информацию по нему')
    return 'get_apt_list'

def get_services_listCommand(update: Update, context):
    return 'get_services'

def monitoring(update: Update, context):
    update.message.reply_text('Вы вошли в раздел *Мониторинга* системы\.', parse_mode='MarkdownV2')
    update.message.reply_text('Команда /get_release - информация о релизе')
    update.message.reply_text('Команда /get_uname - информация о архитектуре процессора, имени хоста системы и версии ядра.')
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
    command ='mpstat'
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
    command = 'ps'
    connect(update, context, command)  

def get_apt_list(update: Update, context):
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
        #update.message.reply_text('Введите название пакета для получения информации')
        user_input = update.message.text
        stdin, stdout, stderr = client.exec_command(f'dpkg -s {user_input} | head -n 20')
        data = stdout.read() + stderr.read()
        client.close()
        update.message.reply_text(data.decode())
        return ConversationHandler.END

def get_ss(update: Update, context):
    command = 'netstat -tuln'
    connect(update, context, command)  

def get_services(update: Update, context):
    command = 'systemctl list-units --type=service | head -n 20'
    connect(update, context, command)  

def findPhoneNumbers(update: Update, context):
    user_input = update.message.text  # Получаем текст, содержащий(или нет) номера телефонов

    phoneNumRegex = re.compile(r'(?:\+7|8)(?: \(\d{3}\) \d{3}-\d{2}-\d{2}|\d{10}|\(\d{3}\)\d{7}| \d{3} \d{3} \d{2} \d{2}| \(\d{3}\) \d{3} \d{2} \d{2}|-\d{3}-\d{3}-\d{2}-\d{2})')  # формат 8 (000) 000-00-00

    phoneNumberList = phoneNumRegex.findall(user_input)  # Ищем номера телефонов

    if not phoneNumberList:  # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return  # Завершаем выполнение функции

    phoneNumbers = ''  # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i + 1}. {phoneNumberList[i]}\n'  # Записываем очередной номер

    update.message.reply_text(phoneNumbers)  # Отправляем сообщение пользователю
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
    return ConversationHandler.END

def verifyPassword(update: Update, context):
    user_input = update.message.text
    password_regex = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()_\-])[A-Za-z\d!@#$%^&*()_\-]{8,}$')

    if password_regex.match(user_input):
        update.message.reply_text("Пароль сложный.")
    else:
        update.message.reply_text("Пароль простой.")
    return ConversationHandler.END


def echo(update: Update, context):
    update.message.reply_text(update.message.text)


def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('findPhoneNumbers', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],

        },
        fallbacks=[]
    )
    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('findEmails', findEmailsCommand)],
        states={
            'findEmails': [MessageHandler(Filters.text & ~Filters.command, findEmails)],
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
    #dp.add_handler(CommandHandler("get_apt_list", get_apt_list))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_services", get_services))

    # Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
