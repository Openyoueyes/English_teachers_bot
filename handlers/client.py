from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from data.config import ADMINS,ID_GROUP
from handlers.admin import start_menu
from keyboards.client_kb import kb_client_registration, kb_client_pay, kb_client_payments, kb_client_cancel
from database import postgres_db
from states.states import Registration, FSMPay, FSMclient
from create_bot import bot


async def command_start(message: types.Message, state: FSMContext):
    await state.finish()
    full_name = postgres_db.sql_verification_user(message.from_user.id)
    if full_name is not None:
        await bot.send_message(
            message.from_user.id, f"Hello, my dear student "
                                  f"{full_name.split()[0]}❤️", reply_markup=kb_client_pay)
        await message.delete()
        await FSMclient.waiting_start_menu_commands.set()
    else:
        await bot.send_message(message.from_user.id, f"Hello {message.from_user.first_name},"
                                                     " First step 1️⃣  Please click «Register»",
                               reply_markup=kb_client_registration)
        await Registration.waiting_button_registration.set()
        await message.delete()


async def cansel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.reply('Ok!', reply_markup=kb_client_pay)
        return
    await state.finish()
    await FSMclient.waiting_start_menu_commands.set()
    await message.reply('Ok!', reply_markup=kb_client_pay)


async def registration(message: types.Message):
    if message.text == "🤝Register":
        full_name = postgres_db.sql_verification_user(message.from_user.id)
        if full_name is not None:
            await message.answer("You have registration", reply_markup=kb_client_pay)
        else:
            await message.answer("Second step 2️⃣ Please write your name and surname")
            await Registration.next()
    else:
        await message.answer("Command is wrong!")


async def fsm_full_name(message: types.Message, state: FSMContext):
    if all(map(lambda x: x.isalpha(), message.text.split())) and len(message.text.split()) == 2:
        await state.update_data(full_name=message.text)
        await state.update_data(tg_id=message.from_user.id)
        user_data = await state.get_data()
        postgres_db.sql_registration(user_data['tg_id'], user_data['full_name'])
        await state.finish()
        await bot.send_message(message.from_user.id, "Thanks for registration 😊", reply_markup=kb_client_pay)
        await FSMclient.waiting_start_menu_commands.set()
    else:
        await message.answer("Enter correct full name.For example: 'Ivan Ivanov'")


async def choose_start_menu_command(message: types.Message, state: FSMContext):
    if message.text == "🧾Confirm payment":
        await state.finish()
        await message.reply('How many lessons did you pay?'
                            '\nWrite the number ⬇️',
                            reply_markup=kb_client_payments)
        await FSMPay.waiting_amount_lessons.set()
    elif message.text == "💼Check balance":
        st_id = postgres_db.student_id_check(message.from_user.id)
        info = postgres_db.sql_all_payments_student_info(st_id)
        if len(info["all_lessons_mark_check"]) == 0:
            await message.answer(f"\nBalance: {info['student_balance']} byn", reply_markup=kb_client_pay)
        elif len(info["all_lessons_mark_check"]) == 1:
            await message.answer(f"\nBalance: {info['student_balance']} byn", reply_markup=kb_client_pay)
        else:
            await message.answer(f"\nBalance: {info['student_balance']} byn", reply_markup=kb_client_pay)


async def pay_lessons(message: types.Message, state: FSMContext):
    if message.text.isdigit() and int(message.text) > 0:
        async with state.proxy() as data:
            data['amount_lessons'] = message.text
            await FSMPay.next()
            await message.reply('Upload the receipt 📸'
                                ' It must be a screenshot or a photo.', reply_markup=kb_client_cancel)
    elif message.text == "◀️Back":
        await message.answer('Ok!', reply_markup=kb_client_pay)
        await state.finish()
        await FSMclient.waiting_start_menu_commands.set()
    else:
        await message.answer("Command is wrong.Write the number ⬇️")


async def load_photo(message: types.Message, state: FSMContext):
    st_id = postgres_db.student_id_check(message.from_user.id)
    full_name = postgres_db.sql_full_name_check(str(st_id))
    data = await state.get_data()
    amount = data['amount_lessons']
    if int(st_id) in (1, 3, 5, 13):
        lesson_cost = 35
    elif int(st_id) == 8:
        lesson_cost = 50
    else:
        lesson_cost = 30
    amount = int(amount) * lesson_cost
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id
    data = await state.get_data()
    photo = data['photo']
    postgres_db.sql_pay_many_lesson(st_id, photo, amount)
    all_payments_info = postgres_db.sql_all_payments_student_info(st_id)
    lessons_mark_count_fnc = int(all_payments_info['no_use_money'] / lesson_cost)
    lessons_no_mark_check_count = all_payments_info['all_lessons_no_mark_check_count']
    count_func = lessons_mark_count_fnc if \
        lessons_mark_count_fnc <= int(lessons_no_mark_check_count) else int(lessons_no_mark_check_count)
    if lessons_mark_count_fnc >= 1:
        iterator = (i for i in range(count_func))
        for _ in iterator:
            pay_id = str(postgres_db.sql_check_mark_payment_id(
                st_id,
                all_payments_info['balance_of_last_use_payment_id'],
                all_payments_info['all_payments_lst'],
                all_payments_info['last_use_payment_id']))
            postgres_db.sql_mark_payment_id(str(st_id), pay_id)
            all_payments_info = postgres_db.sql_all_payments_student_info(st_id)
    await message.reply('Thanks for your payment 😊 Have a nice day ☀️', reply_markup=kb_client_pay)
    await bot.send_message(int(ID_GROUP), f"Student {full_name} made a payment in the amount {amount}")
    await state.finish()
    await FSMclient.waiting_start_menu_commands.set()


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start', 'help'], state='*')
    dp.register_message_handler(cansel_handler, lambda message: 'Cancel' in message.text, state="*")
    dp.register_message_handler(start_menu, Text(equals='admin'), user_id=ADMINS, state="*")
    dp.register_message_handler(cansel_handler, Text(equals='Cancel', ignore_case=True), state='*')
    dp.register_message_handler(registration, state=Registration.waiting_button_registration)
    dp.register_message_handler(fsm_full_name, state=Registration.waiting_full_name)
    dp.register_message_handler(choose_start_menu_command, state=FSMclient.waiting_start_menu_commands)
    dp.register_message_handler(pay_lessons, state=FSMPay.waiting_amount_lessons)
    dp.register_message_handler(load_photo, content_types=['photo'], state=FSMPay.waiting_for_receipt)
