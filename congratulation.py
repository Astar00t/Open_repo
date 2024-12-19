#импорты
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
import asyncio
import random

#типа база поздравлений и юзеров и тд
congr_list: dict[str: list[str]] = {'new_year': ['Поздравление №1', 'Поздравление №2', 'Поздравление №3'],
                                    'birth': ['Поздравление №4', 'Поздравление №5', 'Поздравление №6'],
                                    'bastille': ['Поздравление №7', 'Поздравление №8', 'Поздравление №9',
                                                 'Поздравление №10']}
user_list = {}
bot_token = ''


#Возможно, fsm здесь излишне, но мне лень сейчас придумывать фильтры
class FsmName(StatesGroup):
    name_1 = State()
    name_2 = State()


#Пользовательский роутер
user_router = Router()


#Команда старт
@user_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext):
    await message.answer(text='\tЭто бот по составлению поздравлений.\n'
                              'Он знает целых три праздника:\n'
                              'Новый год, день рождения и день взятия Бастилии.\n'
                              'Напишите имя того, кого хотите поздравить.')
    if message.from_user.id not in user_list:
        user_list[message.from_user.id] = {'name_1': None,
                                           'name_2': None}
    await state.set_state(FsmName.name_1)


#Введено первое имя, просим второе
@user_router.message(StateFilter(FsmName.name_1), F.text.isalpha())
async def name_1_input(message: Message, state: FSMContext):
    user_list[message.from_user.id]['name_1'] = message.text
    await message.answer(text='Прекрасно! Теперь напишите ваше имя, чтобы я мог добавить его в конце.')
    await state.set_state(FsmName.name_2)


#Введено второе имя, делаем выбор праздника на кнопках
@user_router.message(StateFilter(FsmName.name_2), F.text.isalpha())
async def name_2_input(message: Message, state: FSMContext):
    user_list[message.from_user.id]['name_2'] = message.text
    await state.clear()
    new_button = InlineKeyboardButton(text="Новый год", callback_data='new_year')
    birth_button = InlineKeyboardButton(text='День рождения', callback_data='birth')
    bastille_button = InlineKeyboardButton(text='День взятия Бастилии', callback_data='bastille')
    keyboard: list[list[InlineKeyboardButton]] = [[new_button, birth_button], [bastille_button]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer(text='Замечательно! А сейчас выберите праздник, с которым желаеете поздравить.',
                         reply_markup=markup)


#Собираем поздравление
@user_router.callback_query(F.data.in_(['new_year', 'birth', 'bastille']))
async def combin_process(callback: CallbackQuery):
    await callback.message.answer(text=f'\t{user_list[callback.from_user.id]['name_1']}'
                                       f'\n{random.choice(congr_list[callback.data])}'
                                       f'\n\t{user_list[callback.from_user.id]['name_2']}')


#Основная функция
async def main():
    bot = Bot(token=bot_token)
    dp = Dispatcher()
    dp.include_router(user_router)
    await dp.start_polling(bot)


#Запускаем
if __name__ == '__main__':
    asyncio.run(main())
