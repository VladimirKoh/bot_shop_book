import csv
import random
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
# from apscheduler.schedulers.asyncio import AsyncIOSchedulerip
from dotenv import load
from sqllite import Database
from yandex_pay import payment_yandex, sucsess_pay
import os


load()

storage = MemoryStorage()
bot = Bot(token=os.getenv('TOKEN'), parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot=bot, storage=storage)
db = Database('database.db')


PRICE_BOOK = 500
PRICE_BOOK_TEST = 10


class StateUsersData(StatesGroup):
    promo_code_state = State()


def get_keyboard_buy():
    ikb = InlineKeyboardMarkup(row_width=1)
    ib = InlineKeyboardButton('📚 Купить книгу', callback_data='buy_book')
    ikb.add(ib)
    return ikb


def get_keyboard_buy_book(summa, label_user):
    ikb = InlineKeyboardMarkup(row_width=1)
    ib = InlineKeyboardButton('💳 Оплатить', url=payment_yandex(summa, label_user))
    ib1 = InlineKeyboardButton('✅ Я ОПЛАТИЛ', callback_data=f"check_pay_{label_user}")
    ikb.add(ib, ib1)
    return ikb


# def get_keyboard_channel():
#     ikb = InlineKeyboardMarkup(row_width=1)
#     ib = InlineKeyboardButton('📚 ЗАБРАТЬ КНИГУ', url='https://t.me/+OUYy6zhO8DE0MWYy')
#     ikb.add(ib)
#     return ikb


def get_keyboard_yes():
    rkb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb = KeyboardButton('У меня нет промокода 😔')
    rkb.add(kb)
    return rkb


def get_keyboard_next():
    rkb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb = KeyboardButton('У меня нет промокода 😔')
    rkb.add(kb)
    return rkb

# async def apschedule_check_pay():
#     await sucsess_pay()


@dp.message_handler(commands='start')
async def command_start_process(message: types.Message):
    # db.create_tables()
    parent = message.text[7:]
    if not db.user_exists(message.from_user.id):
        db.add_user(message.from_user.id, parent, message.from_user.username)
    text = f"Здравствуйте, рады приветствовать Вас! Здесь вы сможете купить авторску книгу, которую написал человек будучи в длительном запое, который длился приблизительно 3 месяца\n\n<b>Как стать миллионером?</b>\n\nАвтор книги: <b>Арнольд Кох</b>\n\nСтоимость всего <b>{PRICE_BOOK}</b> рублей"
    await message.answer_photo(photo="https://2books.su/assets/img/covers/the-snow-queen-adapted.jpg",
                               caption=text, 
                               reply_markup=get_keyboard_buy())


# @dp.message_handler(commands='check')
# async def check_pay(message: types.Message):
#     await message.answer('✅ Платеж успешно прошел, держи свою книгу')
#     db.set_pay(message.from_user.id)
#     await bot.send_document(chat_id=message.from_user.id, document=open("./Book_by_Test.pdf", "rb"), caption="Какой то текст описание книги")


@dp.message_handler(commands=['friends'])
async def get_friends(message: types.Message):
    result = db.get_parent(message.from_user.id)
    text = f"Ваша парнерская ссылка:\nhttps://t.me/HitchhikerRussia_bot?start={message.from_user.id}\n\nПо вашей ссылке зарегистрировалось {len(result)} человек"
    await message.answer(text, reply_markup=ReplyKeyboardRemove())


@dp.message_handler(commands=['add_promo_code'])
async def add_promocode(message: types.Message):
    try:
        command, promocode, procent = message.text.split()
        db.add_promocode(promocode, procent)
        await message.answer(f'Промокод {promocode} на скидку {procent}% добавлен')
    except Exception as e:
        await message.answer('Нужно ввести /add_promo_code НАЗВАНИЕ(ТЕКСТ АНГЛ ИЛИ РУС) ПРОЦЕНТ СКИДКИ(ЧИСЛО) ')


@dp.message_handler(commands=['del_promo_code'])
async def add_promocode(message: types.Message):
    try:
        command, id = message.text.split()
        db.del_promocode(id)
        await message.answer(f'Промокод удален \nПосомтреть список промокодов\n/get_promocode')
    except Exception as e:
        await message.answer('Нужно ввести /del_promo_code АЙДИ ПРОМОКОДА')


@dp.message_handler(commands=['get_users'])
async def get_users_in_file(message: types.Message):
    await message.answer('Вы запросили список всех пользователей.\nОжидайте...')
    result = db.get_users()
    print(result)
    fields = ['user_id', 'parent', 'pay']; 
    with open('users.csv', 'w', encoding='utf-8-sig', newline='') as state_file:
        writer = csv.writer(state_file, fields, delimiter=';')
        writer.writerows(result)
    with open('users.csv', 'rb') as state_file:
        await message.answer_document(state_file)


@dp.message_handler(commands=['get_promocode'])
async def get_users_in_file(message: types.Message):
    result = db.get_promocode()
    if result:
        text = list()
        for promo in result:
            text.append(f"id <b>{promo[0]}</b> {promo[1]} скидка {promo[2]}%\n")
        text.append(f"Чтобы удалить промокод введите /del_promo_code и ID")
        final_text = "".join(text)
        await message.answer(final_text)
    else:
        await message.answer('У вас еще нет промокодов')


@dp.message_handler(Text(equals='У меня нет промокода 😔'), state='*')
async def no_promocode(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer('Очень жаль, что у вас нет промокода 😔', reply_markup=ReplyKeyboardRemove())
    await state.finish()
    label = int(message.from_user.id) + random.randint(10, 99)
    text = f"""Стоимость книги <b>{PRICE_BOOK}</b> рублей
Скидка по промокоду: <b>нет</b>

<b>Итого к оплате: {PRICE_BOOK} рублей</b>"""
    await message.answer(text, reply_markup=get_keyboard_buy_book(PRICE_BOOK_TEST, label))


@dp.message_handler(state=StateUsersData.promo_code_state)
async def waiting_promocode(message: types.Message, state: FSMContext):
    result = db.check_promo_code(message.text)
    if result:
        await message.answer('✅ Ваш промокод успешно применен', reply_markup=ReplyKeyboardRemove())
        sale = int(result[-1])
        await state.update_data(procent=sale)
        final_price = PRICE_BOOK - (PRICE_BOOK / 100 * sale)
        label = int(message.from_user.id) + random.randint(10, 99)
        text = f"""Стоимость книги <b>{PRICE_BOOK}</b> рублей
Скидка по промокоду: <b>{sale}%</b>

<b>Итого к оплате: {int(final_price)} рублей</b>"""
        await message.answer(text, reply_markup=get_keyboard_buy_book(PRICE_BOOK_TEST, label))
        await state.finish()
    else:
        await message.answer('К сожалению промокод не найден\nПопробуйте ввести еще раз или нажмите\nУ меня нет промокода', reply_markup=get_keyboard_next())


@dp.callback_query_handler(Text(equals='buy_book'))
async def callback_buy_book(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Если у вас есть промокод на скидку введите его в чат', reply_markup=get_keyboard_yes())
    await state.set_state(StateUsersData.promo_code_state.state)


@dp.callback_query_handler(Text(startswith='check_pay_'))
async def callback_check_balance_pay(callback: types.CallbackQuery):
    label = callback.data.split('_')[-1]
    result = sucsess_pay(label)
    if result:
        await callback.message.answer('✅ Платеж успешно прошел, держи свою книгу')
        await bot.send_document(chat_id=callback.from_user.id, document=open("./Book_by_Test.pdf", "rb"), caption="Какой то текст описание книги")
        db.set_pay(callback.from_user.id)
    else:
        await callback.answer('⚠️ Платеж не найден\nПопробуйте проверить через несколько секунд.', show_alert=True)


if __name__ == '__main__':
    # scheduler = AsyncIOScheduler() # при заливке на сервер убирать тайм зону
    # scheduler.add_job(apschedule_check_pay, "cron", seconds=5)
    # scheduler.start()
    executor.start_polling(dp, skip_updates=True)