from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from data.config import ADMINS
from database import postgres_db
from keyboards.admin_kb import admin_start_kb, admin_payments_kb, \
    admin_students_kb, admin_lessons_kb, admin_student_payment_kb, kb_admin_cancel, admin_student_lessons_kb, \
    mark_lesson_admin_kb, lessons_view_admin_kb, admin_income_kb
from states.states import FSM_admin, Payments, Students, Lessons_mark, Lessons_view, Lessons, Income
from create_bot import bot


async def start_menu(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Hello, Teacher!', reply_markup=admin_start_kb)
    await FSM_admin.waiting_start_menu_commands.set()


async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.answer('Cancelled.', reply_markup=admin_start_kb)
    await FSM_admin.waiting_start_menu_commands.set()


async def start_menu_cmd(message: types.Message, state: FSMContext):
    await state.finish()
    if message.text == "💵Income":
        await message.answer('Choose category:', reply_markup=admin_income_kb)
        await Income.waiting_start_income_commands.set()
    elif message.text == "💰Payments":
        await message.answer('Choose category:', reply_markup=admin_payments_kb)
        await Payments.waiting_start_payments_commands.set()  # 1 -ое
    elif message.text == "👨‍🎓Students":
        await message.answer('Choose category:', reply_markup=admin_students_kb)
        await Students.waiting_start_students_commands.set()
    elif message.text == "📚Lessons":
        await message.answer('Choose category:', reply_markup=admin_lessons_kb)
        await Lessons.waiting_start_lessons_commands.set()

    elif message.text == "🔲Debtors":
        student_no_mark = postgres_db.sql_debtors()
        if student_no_mark:
            dolgi = {}
            for i in student_no_mark:
                dolgi.setdefault(i[1], [])
                dolgi[i[1]].append(i[2])
            if dolgi:
                await bot.send_message(message.from_user.id, "######DEBTORS_START######")
                for key, value in dolgi.items():
                    await bot.send_message(message.from_user.id, f"Student {key} must pay {len(dolgi[key])} lesson")
                await bot.send_message(message.from_user.id, "######DEBTORS_FINISH######")
        else:
            await bot.send_message(message.from_user.id, f"No debtors!It's okay!")
        await message.answer("Anything else?", reply_markup=admin_start_kb)
        await FSM_admin.waiting_start_menu_commands.set()
    else:
        await message.answer('Wrong command')
        await FSM_admin.waiting_start_menu_commands.set()


async def income_menu(message: types.Message, state: FSMContext):
    if message.text == "🌜Current month":
        cur_mounth_income = postgres_db.my_income_curr()
        await bot.send_message(message.from_user.id, f"Income: {cur_mounth_income[0][0]}")
        await bot.send_message(message.from_user.id, "OK!", reply_markup=admin_start_kb)
        await state.finish()
        await FSM_admin.waiting_start_menu_commands.set()
    elif message.text == "🌛Previous month":
        prev_mounth_income = postgres_db.my_income_prev()
        await bot.send_message(message.from_user.id, f"Income: {prev_mounth_income[0][0]}")
        await bot.send_message(message.from_user.id, "OK!", reply_markup=admin_start_kb)
        await state.finish()
        await FSM_admin.waiting_start_menu_commands.set()
    elif message.text == "◀️Back":
        await bot.send_message(message.from_user.id, "OK!", reply_markup=admin_start_kb)
        await state.finish()
        await FSM_admin.waiting_start_menu_commands.set()


async def students_menu(message: types.Message, state: FSMContext):
    if message.text == "👨‍💻 Show students and their balance":
        students_info = postgres_db.sql_show_all_students()
        for student in students_info:
            all_payments_student_info = postgres_db.sql_all_payments_student_info(student[0])
            await bot.send_message(message.from_user.id,
                                   f"ID:{student[0]} {student[1]}, balance: "
                                   f"{all_payments_student_info['student_balance']} BYN, registration: {student[3]}")

        await bot.send_message(message.from_user.id, "OK!", reply_markup=admin_start_kb)
        await state.finish()
        await FSM_admin.waiting_start_menu_commands.set()
    elif message.text == "◀️Back":
        await bot.send_message(message.from_user.id, "OK!", reply_markup=admin_start_kb)
        await state.finish()
        await FSM_admin.waiting_start_menu_commands.set()


async def lessons_menu(message: types.Message, state: FSMContext):
    await state.finish()
    if message.text == "📕 Mark lessons":
        await message.answer("Ok!", reply_markup=mark_lesson_admin_kb)
        await Lessons_mark.waiting_mark_lessons_command.set()
    elif message.text == "📙 View lessons":
        await message.answer('Ok!', reply_markup=lessons_view_admin_kb)
        await Lessons_view.waiting_view_lessons_command.set()
    elif message.text == "◀️Back":
        await bot.send_message(message.from_user.id, "OK!", reply_markup=admin_start_kb)
        await FSM_admin.waiting_start_menu_commands.set()


async def mark_lesson_menu(message: types.Message, state: FSMContext):
    if message.text == "💁‍ Choose student":
        all_students = postgres_db.sql_show_all_students()
        for student in all_students:
            await bot.send_message(message.from_user.id,
                                   f"ID:{student[0]} {student[1]}")
        await message.answer('Enter student ID:', reply_markup=kb_admin_cancel)
        await Lessons_mark.next()
    if message.text == "◀️Back":
        await bot.send_message(message.from_user.id, "OK!", reply_markup=admin_start_kb)
        await state.finish()
        await FSM_admin.waiting_start_menu_commands.set()


async def mark_lesson(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['student_id'] = message.text
    data = await state.get_data()
    st_id = data['student_id']
    full_name = postgres_db.sql_full_name_check(st_id)
    if full_name is not None:
        async with state.proxy() as data:
            data['full_name'] = full_name
        await message.reply(f"You choose {full_name}")
        postgres_db.sql_mark_lesson(st_id)
        all_payments_info = postgres_db.sql_all_payments_student_info(st_id)
        if int(st_id) in (1, 3, 5, 13):
            lesson_cost = 35
        elif int(st_id) == 8:
            lesson_cost = 50
        else:
            lesson_cost = 30
        lessons_mark_count_fnc = int(all_payments_info['no_use_money'] / lesson_cost)
        lessons_no_mark_check_count = all_payments_info['all_lessons_no_mark_check_count']
        await message.answer(f"Create lesson for payment.\nStudent: {full_name}", reply_markup=admin_start_kb)
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
                postgres_db.sql_mark_payment_id(st_id, pay_id)
                all_payments_info = postgres_db.sql_all_payments_student_info(st_id)
            await message.answer(f"Mark success, student balance:"
                                 f" {all_payments_info['student_balance']}",
                                 reply_markup=admin_start_kb)
        else:
            await message.answer(f"Mark filed, student balance:"
                                 f" {all_payments_info['student_balance']}",
                                 reply_markup=admin_start_kb)
        await state.finish()
        await FSM_admin.waiting_start_menu_commands.set()
    else:
        await message.answer("🛑 Wrong command.Enter correct student ID:")


async def lessons_view_menu(message: types.Message, state: FSMContext):
    if message.text == "📓Show all lessons per month":
        all_stundet_lesson_per_mounth = postgres_db.sql_all_lessons_students()
        if all_stundet_lesson_per_mounth:
            for lesson in all_stundet_lesson_per_mounth:
                await bot.send_message(message.from_user.id, f"Lesson id:{lesson[0]} Student :{lesson[1]},"
                                                             f"\nLesson date: {lesson[2]}")
        else:
            await message.answer("Student doesn't have lessons", reply_markup=admin_lessons_kb)
            
    elif message.text == "💁‍ Choose student":
        all_students = postgres_db.sql_show_all_students()
        for student in all_students:
            await bot.send_message(message.from_user.id,
                                   f"ID:{student[0]} {student[1]}")
        await message.answer('Enter student ID:', reply_markup=kb_admin_cancel)
        await Lessons_view.next()
    if message.text == "◀️Back":
        await bot.send_message(message.from_user.id, "OK!", reply_markup=admin_start_kb)
        await state.finish()
        await FSM_admin.waiting_start_menu_commands.set()


async def lessons_view_check_student_id(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['student_id'] = message.text
    data = await state.get_data()
    st_id = data['student_id']
    full_name = postgres_db.sql_full_name_check(st_id)
    if full_name is not None:
        async with state.proxy() as data:
            data['full_name'] = full_name
        await message.reply(f"You choose {full_name}", reply_markup=admin_student_lessons_kb)
        await Lessons_view.next()
    else:
        await message.answer("🛑 Wrong command.Enter correct student ID:")


async def lessons_view_menu_per_student(message: types.Message, state: FSMContext):
    data = await state.get_data()
    st_id = data['student_id']
    if message.text == "📓 Show all student lessons":
        all_student_lessons = postgres_db.sql_all_lessons_student(st_id)
        if all_student_lessons:
            for lesson in all_student_lessons:
                await bot.send_message(message.from_user.id, f"Lesson id:{lesson[0]} Student :{lesson[1]},"
                                                         f"\nLesson date: {lesson[2]}")
        else:
            await message.answer("Student doesn't have lessons", reply_markup=lessons_view_admin_kb)
        await message.answer("Ok!", reply_markup=lessons_view_admin_kb)
        await state.finish()
        await Lessons_view.waiting_view_lessons_command.set()
    elif message.text == "📅 Monthly lessons":
        interval = '30'
        mounth_student_lessons = postgres_db.sql_show_student_lessons_per_date(st_id, interval)
        if mounth_student_lessons:
            for lesson in mounth_student_lessons:
                await bot.send_message(message.from_user.id, f"Lesson id:{lesson[0]} "
                                                             f"Student :{lesson[1]},\nLesson date: {lesson[2]}")
        else:
            await message.answer("Student doesn't have lessons", reply_markup=lessons_view_admin_kb)
        await message.answer("Ok!", reply_markup=lessons_view_admin_kb)
        await state.finish()
        await Lessons_view.waiting_view_lessons_command.set()
    elif message.text == "🗒 Lessons per week":
        interval = '6'
        week_student_lessons = postgres_db.sql_show_student_lessons_per_date(st_id, interval)
        if week_student_lessons:
            for lesson in week_student_lessons:
                await bot.send_message(message.from_user.id, f"Lesson id:{lesson[0]} "
                                                             f"Student :{lesson[1]},\nLesson date: {lesson[2]}")
        else:
            await message.answer("Student doesn't have lessons", reply_markup=lessons_view_admin_kb)
        await message.answer("Ok!", reply_markup=admin_payments_kb)
        await state.finish()
        await Lessons_view.waiting_view_lessons_command.set()
    elif message.text == "◀️Back":
        await message.answer("Ok!", reply_markup=lessons_view_admin_kb)
        await Lessons_view.previous()  # Выход в 2 состояние
        await Lessons_view.previous()
    else:
        await message.answer("🛑 Wrong command.")


async def payments_menu(message: types.Message, state: FSMContext):
    if message.text == "🏦All payments per month":
        all_mounth_payments = postgres_db.sql_show_all_payments()
        if all_mounth_payments:
            for ret in all_mounth_payments:
                await bot.send_photo(message.from_user.id, ret[2],
                                     f'Payment id: {ret[0]}\nStudent: {ret[1]}\nPayment date: {ret[3]}\n'
                                     f'Amount: {ret[4]}')
        else:
            await bot.send_message(message.from_user.id, "Payments list is empty!")
    elif message.text == "💁‍ Choose student":
        all_students = postgres_db.sql_show_all_students()
        for student in all_students:
            await bot.send_message(message.from_user.id,
                                   f"ID:{student[0]} {student[1]}")
        await message.answer('Enter student ID:', reply_markup=kb_admin_cancel)
        await Payments.next()  # 2-e
    elif message.text == "◀️Back":
        await bot.send_message(message.from_user.id, "OK!", reply_markup=admin_start_kb)
        await state.finish()
        await FSM_admin.waiting_start_menu_commands.set()


async def payments_student(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['student_id'] = message.text
    data = await state.get_data()
    st_id = data['student_id']
    full_name = postgres_db.sql_full_name_check(st_id)
    if full_name is not None:
        async with state.proxy() as data:
            data['full_name'] = full_name
        await message.reply(f"You choose {full_name}", reply_markup=admin_student_payment_kb)
        await Payments.next()
    else:
        await message.answer("🛑 Wrong command.Enter correct student ID:")


async def all_student_payment_menu(message: types.Message, state: FSMContext):
    data = await state.get_data()
    st_id = data['student_id']
    if message.text == "🧾 All student payments":
        all_student_payments = postgres_db.sql_show_student_payments(st_id)
        if all_student_payments:
            for ret in all_student_payments:
                await bot.send_photo(message.from_user.id, ret[2],
                                     f'Payment id: {ret[0]}\nFull name: {ret[1]}\nPayment date: {ret[3]}\n'
                                     f'Amount: {ret[4]}')
        else:
            await message.answer("Student doesn't have payments", reply_markup=admin_payments_kb)
        await message.answer("Ok!", reply_markup=admin_payments_kb)
        await state.finish()
        await Payments.waiting_start_payments_commands.set()
    elif message.text == "📅 Monthly payments":
        interval = '30'
        mounth_student_payements = postgres_db.sql_show_student_payments_per_date(st_id, interval)
        if mounth_student_payements:
            for ret in mounth_student_payements:
                await bot.send_photo(message.from_user.id, ret[2],
                                     f'Payment id: {ret[0]}\nFull name: {ret[1]}\nPayment date: {ret[3]}\n'
                                     f'Amount: {ret[4]}')
        else:
            await message.answer("Student doesn't have payments", reply_markup=admin_payments_kb)
        await message.answer("Ok!", reply_markup=admin_payments_kb)
        await state.finish()
        await Payments.waiting_start_payments_commands.set()
    elif message.text == "🗒 Payments per week":
        interval = '6'
        week_student_payments = postgres_db.sql_show_student_payments_per_date(st_id, interval)
        if week_student_payments:
            for ret in week_student_payments:
                await bot.send_photo(message.from_user.id, ret[2],
                                     f'Payment id: {ret[0]}\nFull name: {ret[1]}\nPayment date: {ret[3]}\n'
                                     f'Amount: {ret[4]}')
        else:
            await message.answer("Student doesn't have payments", reply_markup=admin_payments_kb)
        await message.answer("Ok!", reply_markup=admin_payments_kb)
        await state.finish()
        await Payments.waiting_start_payments_commands.set()
    elif message.text == "◀️Back":
        await message.answer("Ok!", reply_markup=admin_payments_kb)
        await Payments.previous()
        await Payments.previous()


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(start_menu, Text(equals='admin'), user_id=ADMINS, state="*")
    dp.register_message_handler(start_menu_cmd, user_id=ADMINS, state=FSM_admin.waiting_start_menu_commands)
    dp.register_message_handler(cancel_handler, commands='cancel', user_id=ADMINS, state="*")
    dp.register_message_handler(cancel_handler, Text(equals='cancel', ignore_case=True), user_id=ADMINS, state="*")
    dp.register_message_handler(payments_menu, user_id=ADMINS, state=Payments.waiting_start_payments_commands)
    dp.register_message_handler(students_menu, user_id=ADMINS, state=Students.waiting_start_students_commands)
    dp.register_message_handler(income_menu, user_id=ADMINS, state=Income.waiting_start_income_commands)
    dp.register_message_handler(lessons_menu, user_id=ADMINS, state=Lessons.waiting_start_lessons_commands)
    dp.register_message_handler(mark_lesson_menu, user_id=ADMINS, state=Lessons_mark.waiting_mark_lessons_command)
    dp.register_message_handler(mark_lesson, user_id=ADMINS, state=Lessons_mark.waiting_student_id_mark)
    dp.register_message_handler(payments_student, user_id=ADMINS, state=Payments.waiting_student_id)
    dp.register_message_handler(all_student_payment_menu, user_id=ADMINS, state=Payments.waiting_waiting_full_name)
    dp.register_message_handler(lessons_view_menu, user_id=ADMINS, state=Lessons_view.waiting_view_lessons_command)
    dp.register_message_handler(lessons_view_check_student_id, user_id=ADMINS, state=Lessons_view.waiting_student_id)
    dp.register_message_handler(lessons_view_menu_per_student,
                                user_id=ADMINS, state=Lessons_view.waiting_final_view_command)
