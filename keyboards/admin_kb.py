from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Начальная клавиатура админа
payments_info = KeyboardButton('💰Payments')
lessons_info = KeyboardButton('📚Lessons')
students_info = KeyboardButton('👨‍🎓Students')
debtors_info = KeyboardButton('🔲Debtors')
income_info = KeyboardButton('💵Income')
admin_start_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True) \
    .add(income_info).add(lessons_info).insert(debtors_info) \
    .add(payments_info).insert(students_info)

# Клавиатура оплат
all_payments = KeyboardButton("🏦All payments per month")
choose_student = KeyboardButton("💁‍ Choose student")
back = KeyboardButton("◀️Back")
admin_payments_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(all_payments) \
    .insert(choose_student).add(back)

# Клавиатура оплат студента
all_student_payment = KeyboardButton("🧾 All student payments")
monthly_payments = KeyboardButton("📅 Monthly payments")
payments_per_week = KeyboardButton("🗒 Payments per week")
admin_student_payment_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(all_student_payment) \
    .insert(monthly_payments).add(payments_per_week).insert(back)
# Клавиатура раздела студент
all_student_list = KeyboardButton("👨‍💻 Show students and their balance")
admin_students_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(all_student_list) \
    .add(back)

view_lesson_button = KeyboardButton("📙 View lessons")
mark_lesson_button = KeyboardButton("📕 Mark lessons")
admin_lessons_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(mark_lesson_button) \
    .insert(view_lesson_button).add(back)

# Клавиатура раздела уроки
all_lessons_list = KeyboardButton("📔 All lessons per week")
view_lessons_admin_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(all_lessons_list) \
    .insert(choose_student).add(back)

mark_lesson_admin_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(choose_student).add(back)
all_students_lessons = KeyboardButton("📓Show all lessons per month")
lessons_view_admin_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True) \
    .add(all_students_lessons).insert(choose_student).add(back)

all_student_lessons = KeyboardButton("📓 Show all student lessons")
monthly_payments = KeyboardButton("📅 Monthly lessons")
payments_per_week = KeyboardButton("🗒 Lessons per week")
admin_student_lessons_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(all_student_lessons) \
    .insert(monthly_payments).add(payments_per_week).insert(back)

cancel_button = KeyboardButton('Cancel')
kb_admin_cancel = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(cancel_button)

current_month_button = KeyboardButton('🌜Current month')
previous_month_button = KeyboardButton('🌛Previous month')
admin_income_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(current_month_button).insert(
    previous_month_button).add(back)
