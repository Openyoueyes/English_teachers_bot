from aiogram.dispatcher.filters.state import State, StatesGroup


class FSM_admin(StatesGroup):
    waiting_start_menu_commands = State()


class Payments(StatesGroup):
    waiting_start_payments_commands = State()
    waiting_student_id = State()
    waiting_waiting_full_name = State()


class Students(StatesGroup):
    waiting_start_students_commands = State()


class Lessons(StatesGroup):
    waiting_start_lessons_commands = State()


class Lessons_mark(StatesGroup):
    waiting_mark_lessons_command = State()
    waiting_student_id_mark = State()


class Lessons_view(StatesGroup):
    waiting_view_lessons_command = State()
    waiting_student_id = State()
    waiting_final_view_command = State()


class FSMclient(StatesGroup):
    waiting_start_menu_commands = State()


class Registration(StatesGroup):
    waiting_button_registration = State()
    waiting_full_name = State()


class FSMPay(StatesGroup):
    waiting_amount_lessons = State()
    waiting_for_receipt = State()


class Income(StatesGroup):
    waiting_start_income_commands = State()
