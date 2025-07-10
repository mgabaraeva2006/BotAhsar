from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters,
    ConversationHandler, CallbackContext
)
from duckduckgo_search import DDGS

# Состояния для ConversationHandler
CHOOSING, MENU_CHOICE, INFO_QUERY = range(3)

menu_items = {
    "1": ("Уаелибаех", "Традиционный осетинский пирог с сыром."),
    "2": ("Цаехаераджын", "Пирог с листьями ботвы, приготовленный по древнему рецепту."),
    "3": ("Картофджын", "Осетинский пирог с начинкой из картофеля и сыра."),
    "4": ("Капускьаджын", "Пирог с капустой, сочный и ароматный."),
    "5": ("Давонджын", "Особый пирог, некого рода экзотика."),
    "6": ("Балджын", "Вкуснейший вишневый пирог."),
    "7": ("Лобиаджын", "Пирог с начинкой из фасоли."),
    "8": ("Хинкали", "Это легендарное блюдо не нуждается в представлении."),
    "9": ("Жыкка", "Народное блюдо из сыра, лучше один раз попробовать, чем сто раз услышать."),
    "10": ("Физонаег", "Осетинский шашлык, приготовленный с особой любовью.")
}

# Генерация клавиатуры для главного меню
def main_keyboard():
    return ReplyKeyboardMarkup(
        [['Подай мне блюдо', 'Я пришел за информацией'], ['Выход']],
        resize_keyboard=True, one_time_keyboard=True
    )

# Клавиатура с блюдами
def menu_keyboard():
    return ReplyKeyboardMarkup(
        [[item[0]] for item in menu_items.values()],
        resize_keyboard=True, one_time_keyboard=True
    )

def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Добро пожаловать в таверну "Осетинские Фыччыны"!\n'
        'Меня зовут Ахсар и здесь мы подаем лучшие блюда Осетинской кухни!\n\n'
        'Чего тебе угодно, незнакомец?',
        reply_markup=main_keyboard()
    )
    return CHOOSING

def choosing(update: Update, context: CallbackContext) -> int:
    ans = update.message.text.strip()
    if ans == 'Подай мне блюдо':
        menu_text = "Ахсар: Вот наше меню, выбирай, что по душе:\n"
        for _, (name, desc) in menu_items.items():
            menu_text += f"{name} — {desc}\n"
        update.message.reply_text(menu_text, reply_markup=menu_keyboard())
        return MENU_CHOICE
    elif ans == 'Я пришел за информацией':
        update.message.reply_text(
            "Так ты пришел в поисках информации. Ты по адресу, не того чего бы не знал мудрый Ахсар.\n"
            "Что тебя интересует?",
            reply_markup=ReplyKeyboardRemove()
        )
        return INFO_QUERY
    elif ans == 'Выход':
        update.message.reply_text("Ахсар: Заходи еще, путник! Удачи в твоих приключениях!", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        update.message.reply_text("Ахсар: Прости, я не понял твой выбор. Попробуй еще раз.", reply_markup=main_keyboard())
        return CHOOSING

def menu_choice(update: Update, context: CallbackContext) -> int:
    choice_name = update.message.text.strip()
    for key, (name, desc) in menu_items.items():
        if choice_name == name:
            update.message.reply_text(
                f"\nАхсар: Отличный выбор! Сейчас подам тебе '{name}'.\nОписание: {desc}\n",
                reply_markup=main_keyboard()
            )
            return CHOOSING

    update.message.reply_text(
        "\nАхсар: Прости, я не знаю такого блюда. Попробуй еще раз.\n",
        reply_markup=menu_keyboard()
    )
    return MENU_CHOICE

def info_query(update: Update, context: CallbackContext) -> int:
    query = update.message.text.strip()
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=3)

    if not results:
        update.message.reply_text("Ахсар: К сожалению здесь моя мудрость тебе не поможет.", reply_markup=main_keyboard())
    else:
        reply = "\nАхсар: Вот чем я могу с тобой поделиться:\n"
        for i, result in enumerate(results, 1):
            reply += f"{i}. {result['title']}\n   {result['href']}\n\n"
        update.message.reply_text(reply, reply_markup=main_keyboard())

    return CHOOSING

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Ахсар: Заходи еще, путник! Удачи в твоих приключениях!', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    TOKEN = '8114763169:AAHYWECH3xDsFH9KQUiMxDE319QT7pFlBnUgit init'

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [MessageHandler(Filters.text & ~Filters.command, choosing)],
            MENU_CHOICE: [MessageHandler(Filters.text & ~Filters.command, menu_choice)],
            INFO_QUERY: [MessageHandler(Filters.text & ~Filters.command, info_query)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
