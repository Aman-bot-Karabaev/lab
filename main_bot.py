
from os import stat
from random import choice
from bot_config import TOKEN
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state  import StatesGroup, State
from aiogram import Bot,Dispatcher,executor,types
from sql.categories_manager1 import MyCategory
from sql.movies_manager import Movies
import mysql.connector
from sql.config import *


bot = Bot(TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot)

class Form(StatesGroup):
    title = State()

def get_connection():
    try:
        connect = mysql.connector.connect(
            host = DATABASE_HOST,
            user = DATABASE_USER,
            password = DATABASE_PASSWORD,
            db  = DATABASE_NAME,
            autocommit = True
        )
    except Exception as e:
        print("Соеденение с базой не установлена.")
        exit(0)
    return connect

# Кнопки
markup = types.ReplyKeyboardMarkup()
categoryies = types.KeyboardButton("🎬Категории фильмов🎬")
movie = types.KeyboardButton("🍿Случайный фильм!🍿")
search = types.KeyboardButton("Поиск🔍")

markup.add(categoryies)
markup.add(movie,search)

@dp.message_handler(commands=['start'])
async def welcome_message(message:types.Message):
    
    text = """
        📍 Лучшие фильмы🎬
📍 Прямая ссылка на просмотр фильмов 🍿
📍 Категории фильмов📀
📍 📢Выберите в меню, что вас интересует:
    """
    await message.reply("🤖Привет,я твой КиноБот!🤖",reply_markup=markup)
    await bot.send_video(message.chat.id, open('IMG_1841.MP4', 'rb'), caption=text)
    

@dp.message_handler(content_types=['text'])
async def welcome_message(message: types.Message):
    if message.text == "🎬Категории фильмов🎬":
        text = "Выберите категорию💥: "
        connect = get_connection()
        cursor = connect.cursor()
        category = MyCategory(cursor)
        categories = category.get_all_categories()
        inline_markup = types.InlineKeyboardMarkup()

        for i in categories:
            button = types.InlineKeyboardButton(i[1], callback_data=f"category_{i[0]}")
            inline_markup.add(button)
        
        await message.answer(text, reply_markup=inline_markup)

# реакция на кнопку рандоный фильм:

    elif message.text == "🍿Случайный фильм!🍿":
        connect = get_connection()
        cursor = connect.cursor()
        movie = Movies(cursor)
        data_ids = movie._get_all_ids()
        ids = [id[0] for id in data_ids]
        print(ids)
        r_id = choice(ids)
        data = movie.get_movies_by_id(r_id)
        data_movie_id = movie.get_movies_by_id(r_id)
        message_text = f"""
        📍Название📍: {data_movie_id[1]} 
    🔖Категория: {data_movie_id[4]} 
    🎞Сюжет: {data_movie_id[2]}🎞
    ⭐️Премьера: {data_movie_id[3]} 

    """
        await message.answer(message_text)

    elif message.text == 'Поиск🔍':
        connect = get_connection()
        cursor = connect.cursor()
        movie = Movies(cursor)
        await message.reply('Введите название: ')


@dp.message_handler(state=Form.title, content_types=['text'])
async def get_search_title(state: FSMContext, message: types.Message):
    async with state.proxy() as data:
        # data['title'] = callback.data
        # print(data['title'])
        print(message)

# Фильмы по категории
@dp.callback_query_handler(lambda c: str(c.data).startswith("category_") )
async def get_movies_by_category(callback: types.CallbackQuery):
    id = int(callback.data[-1])
    connect = get_connection()
    cursor = connect.cursor()
    movie = Movies(cursor)
    
    movies_data = movie.get_movies_by_category(id)
    inline_markup = types.InlineKeyboardMarkup()
    for i in movies_data:
        button = types.InlineKeyboardButton(i[1], callback_data=f"movie_{i[0]}")
        inline_markup.add(button)
    back = types.InlineKeyboardButton("Назад🔙", callback_data="back_category")
    inline_markup.add(back)

    await bot.answer_callback_query(callback.id)
    await callback.message.edit_text(
     "⚡️Список лучших фильмов!⚡️:",
      reply_markup=inline_markup)
  

# Инфо фильма
@dp.callback_query_handler(lambda c: str(c.data).startswith("movie_"))
async def get_movie(callback: types.CallbackQuery):
    movie_id = callback.data.split("_")[-1]
    movie_id = int(movie_id)
    connect = get_connection()
    cursor = connect.cursor()
    movie = Movies(cursor)
    data = movie.get_movies_by_id(movie_id)
    message_text = f"""
        📍Название📍: {data[1]} 
    🔖Категория: {data[4]} 
    🎞Сюжет: {data[2]}🎞
    ⭐️Премьера: {data[3]} 

    """
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Просмотр фильмов онлайн👾", url='https://gidonline.io/')
    back = types.InlineKeyboardButton("Назад🔙", callback_data="back_movies")
    markup.add(back)
    markup.add(button)

    await bot.answer_callback_query(callback.id)
    await callback.message.edit_text(message_text,reply_markup=markup)


# Реакция на кнопку назад:
@dp.callback_query_handler(lambda c: str(c.data).startswith("back_"))
async def get_back(callback):
    data = callback.data.split("_")[1]
    connect = get_connection()
    cursor = connect.cursor()
    if data == "category":
        connect = get_connection()
        cursor = connect.cursor()
        categoryies = MyCategory(cursor)
        data_category = categoryies.get_all_categories()
        text = "Выберите категорию💥: "
        inline_markup = types.InlineKeyboardMarkup()

        for i in data_category:
            button = types.InlineKeyboardButton(i[1], callback_data=f"category_{i[0]}")
            inline_markup.add(button)
        await callback.message.edit_text(text, reply_markup=inline_markup)
    
    
    elif data == 'movies':
        
        connect = get_connection()
        cursor = connect.cursor()
        movie = Movies(cursor)
        
        movies_data = movie.get_movies_by_category(5)
        inline_markup = types.InlineKeyboardMarkup()
        for i in movies_data:
            button = types.InlineKeyboardButton(i[1], callback_data=f"movie_{i[0]}")
            inline_markup.add(button)
        back = types.InlineKeyboardButton("Назад🔙", callback_data="back_category")
        inline_markup.add(back)

        await bot.answer_callback_query(callback.id)
        await callback.message.edit_text(
        "⚡️Список лучших фильмов!⚡️:",
        reply_markup=inline_markup)


# @dp.callback_query_handler()
# Не работает
    # elif data=="movie": 
    #     connect = get_connection()  
    #     cursor = connect.cursor()   
    #     categories = MyCategory(cursor) 
    #     data_category = categories.get_all_categories() 
    #     movie = Movies(cursor)  
    #     for i in data_category:  
    #         category_id = i[0] 
    #     movies_data = movie.get_movies_by_category(category_id)  
    #     inline_markup = types.InlineKeyboardMarkup()  
    #     for i in movies_data:  
    #         button = types.InlineKeyboardButton(i[1], callback_data=f"movie_{i[0]}")  
    #         inline_markup.add(button)  
    #         await callback.message.edit_text("Список фильмов:", reply_markup=inline_markup)



    
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates = True)

