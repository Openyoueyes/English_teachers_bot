import psycopg2 as sq
from datetime import date
from data.config import DB_HOST

base = None


def sql_start():
    global base
    base = sq.connect(dbname="postgres", user="postgres", password="postgres1234512345", host=DB_HOST, port=5432)

    with base:
        with base.cursor() as cur:
            cur.execute('CREATE TABLE IF NOT EXISTS students (student_id serial PRIMARY KEY, '
                        'full_name text NOT NULL, tg_id text UNIQUE, registration_date date)')

            cur.execute('CREATE TABLE IF NOT EXISTS payments (payment_id serial PRIMARY KEY, '
                        'payment_receipt text, payment_date date, student_id int NOT NULL, amount decimal, '
                        'CONSTRAINT fk_payments_students FOREIGN KEY(student_id) REFERENCES students(student_id))')

            cur.execute('CREATE TABLE IF NOT EXISTS lessons (lesson_id serial PRIMARY KEY, '
                        'student_id int NOT NULL, lesson_date date, payment_id int DEFAULT Null,'
                        'CONSTRAINT fk_lessons_payments FOREIGN KEY(payment_id) REFERENCES payments(payment_id),'
                        'CONSTRAINT fk_lessons_students FOREIGN KEY(student_id) REFERENCES students(student_id))')

    if base:
        print("Data base connected OK!")
    else:
        print("Connection filed")


def sql_verification_user(tg_id):
    global base
    with base:
        with base.cursor() as cur:
            cur.execute("SELECT full_name FROM students WHERE tg_id=" + "'" + str(tg_id) + "'")
            full_fetch = cur.fetchall()
            return full_fetch[0][0] if full_fetch else None


def sql_registration(tg_id, full_name):
    global base
    with base:
        with base.cursor() as cur:
            cur.execute("INSERT INTO students(full_name,tg_id,registration_date)\
                VALUES (%s, %s, %s)", (full_name, tg_id, str(date.today())))


def sql_full_name_check(st_id):
    global base
    with base:
        with base.cursor() as cur:
            cur.execute("SELECT full_name FROM students WHERE student_id=" + "'" + st_id + "'")
            line_fetch = cur.fetchone()
            if line_fetch is not None:
                full_name = line_fetch[0]
                return full_name
            return None


def student_id_check(tg_id):
    global base
    with base:
        with base.cursor() as cur:
            cur.execute("SELECT student_id FROM students WHERE tg_id=" + "'" + str(tg_id) + "'")
            line_fetch = cur.fetchone()
            return line_fetch[0]


def no_mark_lst_sql():
    global base
    with base:
        with base.cursor() as cur:
            cur.execute("SELECT students.student_id, students.full_name, students.tg_id, lessons.lesson_id "
                        "FROM students "
                        " LEFT JOIN lessons ON students.student_id=lessons.student_id"
                        " LEFT JOIN payments ON payments.payment_id=lessons.payment_id"
                        " WHERE lessons.payment_id is NULL")
            student_no_mark = cur.fetchall()
            return student_no_mark


def sql_debtors():
    global base
    with base:
        with base.cursor() as cur:
            cur.execute("SELECT students.tg_id, students.full_name,  lessons.lesson_id "
                        "FROM students "
                        " LEFT JOIN lessons ON students.student_id=lessons.student_id"
                        " LEFT JOIN payments ON payments.payment_id=lessons.payment_id"
                        " WHERE lessons.payment_id is NULL and lessons.lesson_id is not NULL")
            student_no_mark = cur.fetchall()
            return student_no_mark


def sql_pay_many_lesson(st_id, photo, amount):
    global base
    with base:
        with base.cursor() as cur:
            cur.execute("INSERT INTO payments(payment_receipt,payment_date,student_id,amount)\
                            VALUES (%s, %s, %s, %s)", (photo, str(date.today()), st_id, amount))


def sql_show_all_payments():
    global base
    with base:
        with base.cursor() as cur:
            cur.execute(
                "SELECT  payments.payment_id, full_name,payments.payment_receipt,payments.payment_date, payments.amount"
                " FROM payments INNER JOIN students ON payments.student_id= students.student_id WHERE payment_date >= date_trunc('month',current_timestamp)")
            full_fetch = cur.fetchall()
            return full_fetch


######rere#####

def sql_show_student_payments(st_id):
    global base
    with base:
        with base.cursor() as cur:
            cur.execute("SELECT  payments.payment_id, full_name,payments.payment_receipt,"
                        "payments.payment_date, payments.amount FROM payments "
                        "LEFT JOIN students ON payments.student_id= students.student_id "
                        "WHERE students.student_id = " + "'" + st_id + "'")
            full_fetch = cur.fetchall()
            return full_fetch


def sql_show_student_payments_per_date(st_id, interval):
    global base
    with base:
        with base.cursor() as cur:
            cur.execute(
                "SELECT  payments.payment_id, full_name,payments.payment_receipt,payments.payment_date, payments.amount "
                "FROM payments LEFT JOIN students ON payments.student_id= students.student_id "
                "WHERE students.student_id=" + "'" + st_id + "'" +
                "AND payments.payment_date >= current_date at time zone 'UTC' - interval '" + interval + " days' ")
            full_fetch = cur.fetchall()
            return full_fetch


def sql_show_all_students():
    global base
    with base:
        with base.cursor() as cur:
            cur.execute("SELECT * FROM students ORDER BY student_id")
            full_fetch = cur.fetchall()
            return full_fetch


def sql_mark_lesson(st_id):
    global base
    with base:
        with base.cursor() as cur:
            # добавляю урок payment_id = Null
            cur.execute("INSERT INTO lessons(student_id,lesson_date) VALUES (%s, %s)", (st_id, date.today()))


# информация о всех платежах студента в виде словаря
def sql_all_payments_student_info(st_id):
    if int(st_id) in (1, 3, 5, 13):
        lesson_cost = 35
    elif int(st_id) == 8:
        lesson_cost = 50
    else:
        lesson_cost = 30
    global base
    with base:
        with base.cursor() as cur:
            # сумма денег всех оплат студента
            cur.execute("SELECT students.student_id, SUM(amount) FROM payments"
                        " LEFT JOIN students ON payments.student_id=students.student_id"
                        " WHERE students.student_id=" + str(st_id) + " GROUP BY students.student_id")
            full_fetch = cur.fetchall()
            sum_all_payments = float(full_fetch[0][1]) if full_fetch else 0
            # все оплаты студента в виде списка payment_id, amount
            cur.execute("SELECT payments.payment_id, amount FROM payments "
                        " LEFT JOIN students ON payments.student_id=students.student_id"
                        " WHERE students.student_id=" + str(st_id) + "")
            all_payments_student = cur.fetchall()
            # все проставленные уроки в виде списка student_id, payment_id, lesson_id
            cur.execute("SELECT students.student_id, "
                        "payments.payment_id, lessons.lesson_id FROM lessons "
                        " LEFT JOIN students ON students.student_id=lessons.student_id"
                        " LEFT JOIN payments ON payments.payment_id=lessons.payment_id"
                        " WHERE students.student_id =" + str(st_id) + " AND lessons.payment_id is not NULL")
            all_lessons_mark_check = cur.fetchall()
            sum_use_money = float(len(all_lessons_mark_check) * lesson_cost) if all_lessons_mark_check else 0
            last_use_payment_id = str(all_lessons_mark_check[-1][1]) if all_lessons_mark_check else str(1)
            # все не проставленные уроки в виде списка student_id, payment_id, lesson_id
            cur.execute("SELECT students.student_id, "
                        "payments.payment_id, lessons.lesson_id FROM lessons "
                        " LEFT JOIN students ON students.student_id=lessons.student_id"
                        " LEFT JOIN payments ON payments.payment_id=lessons.payment_id"
                        " WHERE students.student_id =" + str(st_id) + " AND lessons.payment_id is NULL")
            all_lessons_no_mark_check_list = cur.fetchall()
            all_lessons_no_mark_check_count = len(all_lessons_no_mark_check_list)
            # сумма и список платежей по последнему payment_id который использовали
            cur.execute("SELECT students.student_id, "
                        "payments.payment_id, lessons.lesson_id FROM lessons "
                        " LEFT JOIN students ON students.student_id=lessons.student_id"
                        " LEFT JOIN payments ON payments.payment_id=lessons.payment_id"
                        " WHERE students.student_id =" + str(st_id) + " AND lessons.payment_id=" + last_use_payment_id)
            payments_per_last_use_payment_id_lst = cur.fetchall()
            payments_per_last_use_payment_id_sum = len(payments_per_last_use_payment_id_lst) * lesson_cost \
                if payments_per_last_use_payment_id_lst else 0
            # сумма последней оплаты которая использовалась (запрос по student_id, payment_id)
            cur.execute("SELECT amount FROM payments"
                        " WHERE payment_id =" + last_use_payment_id + " AND student_id=" + str(st_id))
            full_fetch = cur.fetchall()
            sum_last_use_payment_id = float(full_fetch[0][0]) if full_fetch else float(0)
            no_use_money = sum_all_payments - sum_use_money
            balance_of_last_use_payment_id = sum_last_use_payment_id - payments_per_last_use_payment_id_sum
            student_balance = sum_all_payments - sum_use_money - all_lessons_no_mark_check_count * lesson_cost
            all_payments_student_info = dict(all_payments_lst=all_payments_student,
                                             sum_all_payments=sum_all_payments,
                                             all_lessons_no_mark_check_list=all_lessons_no_mark_check_list,
                                             all_lessons_no_mark_check_count=all_lessons_no_mark_check_count,
                                             all_lessons_mark_check=all_lessons_mark_check,
                                             sum_use_money=sum_use_money,
                                             last_use_payment_id=last_use_payment_id,
                                             sum_last_use_payment_id=sum_last_use_payment_id,
                                             no_use_money=no_use_money,
                                             payments_per_last_use_payment_id_lst=payments_per_last_use_payment_id_lst,
                                             payments_per_last_use_payment_id_sum=payments_per_last_use_payment_id_sum,
                                             balance_of_last_use_payment_id=balance_of_last_use_payment_id,
                                             student_balance=student_balance)
            return all_payments_student_info


def sql_check_mark_payment_id(st_id, balance_of_last_use_payment_id, all_payments_lst, last_use_payment_id):
    if int(st_id) in (1, 3, 5, 13):
        lesson_cost = 35
    elif int(st_id) == 8:
        lesson_cost = 50
    else:
        lesson_cost = 30

    if balance_of_last_use_payment_id >= lesson_cost:
        pay_id = last_use_payment_id
        return pay_id
    elif balance_of_last_use_payment_id == 0:
        if last_use_payment_id != 1 and len(all_payments_lst) > 1:
            return all_payments_lst[-1][0]
        else:
            pay_id = all_payments_lst[0][0]
            return pay_id


def sql_mark_payment_id(st_id, p_id):
    global base
    with base:
        with base.cursor() as cur:
            cur.execute("UPDATE lessons SET payment_id=" + p_id +
                        " WHERE lesson_id= (SELECT lesson_id FROM lessons"
                        " WHERE student_id= " + st_id + " AND payment_id is NULL "
                                                        "ORDER BY lesson_id LIMIT 1)")


def sql_all_lessons_students():
    global base
    with base:
        with base.cursor() as cur:
            cur.execute("SELECT lessons.lesson_id, students.full_name, lessons.lesson_date FROM students"
                        " LEFT JOIN lessons ON students.student_id=lessons.student_id"
                        " WHERE Lessons.lesson_date >= current_date at time zone "
                        " 'UTC' - interval '" + "30" + " days' ORDER BY lessons.lesson_id")
            full_fetch = cur.fetchall()
            return full_fetch


def sql_all_lessons_student(st_id):
    global base
    with base:
        with base.cursor() as cur:
            cur.execute("SELECT lessons.lesson_id, students.full_name, lessons.lesson_date FROM students"
                        " LEFT JOIN lessons ON lessons.student_id=students.student_id"
                        " WHERE students.student_id=" + str(st_id) + " ORDER BY lessons.lesson_id")
            full_fetch = cur.fetchall()
            return full_fetch


def sql_show_student_lessons_per_date(st_id, interval):
    global base
    with base:
        with base.cursor() as cur:
            cur.execute(
                "SELECT  lessons.lesson_id, students.full_name, lessons.lesson_date "
                "FROM lessons "
                "LEFT JOIN students ON students.student_id=lessons.student_id "
                "WHERE students.student_id=" + "'" + str(st_id) + "'" +
                "AND lessons.lesson_date >= current_date at time zone "
                " 'UTC' - interval '" + interval + " days' ORDER BY lessons.lesson_id")
            full_fetch = cur.fetchall()
            return full_fetch


def my_income_prev():
    global base
    with base:
        with base.cursor() as cur:
            cur.execute(
                "SELECT SUM(amount) FROM payments "
                "WHERE payment_date >= date_trunc('month',current_timestamp - interval '1 month') "
                "and payment_date <  date_trunc('month',current_timestamp)")
            full_fetch = cur.fetchall()
            return full_fetch


def my_income_curr():
    global base
    with base:
        with base.cursor() as cur:
            cur.execute(
                "SELECT SUM(amount) FROM payments "
                "WHERE payment_date >= date_trunc('month',current_timestamp) ")
            full_fetch = cur.fetchall()
            return full_fetch


async def no_mark_lst(dp):
    student_no_mark = no_mark_lst_sql()
    dolgi = {}
    for i in student_no_mark:
        dolgi.setdefault(i[2], [])
        dolgi[i[2]].append(i[3])
    for key, value in dolgi.items():
        if dolgi[key] != [None] and len(dolgi[key]) == 1:
            try:
                await dp.bot.send_message(int(key), f"I'd like to remind you that"
                                                    f" you have {len(dolgi[key])} an unpaid lesson!"
                                                    f"Please make payment.Thank you 😊")
            except:
                print(f"User: {int(key)} off bot")
        elif dolgi[key] != [None] and len(dolgi[key]) > 1:
            try:
                await dp.bot.send_message(int(key), f"I'd like to remind you that"
                                                    f" you have {len(dolgi[key])} unpaid lessons!"
                                                    f"Please make payment.Thank you 😊")
            except:
                print(f"User: {int(key)} off bot")
