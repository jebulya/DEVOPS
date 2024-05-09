def findEmails(update: Update, context):
    user_input = update.message.text
    
    email_list = re.findall(r'((\s|^)[0-9a-zA-z]+@[0-9a-zA-z]+\.[0-9a-zA-z]+(\s|$))', user_input)

    if not email_list:
        update.message.reply_text('Адреса почты не найдены')
        return

    phoneNumbers = ''
    for i in range(len(email_list)):
        phoneNumbers += f'{i + 1}. {email_list[i][0]}\n'

    update.message.reply_text(phoneNumbers)
    return ConversationHandler.END