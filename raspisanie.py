from selenium import webdriver as wd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs

import time
from datetime import datetime, date, time, timedelta
import json
import os.path
import sys

sys.path.append('C:\\Users\\truel\\AppData\\Local\\Programs\\Python')

# from MyMods.ERP import ShablonReply as sr
# from MyMods.ERP import SimpleFunks as smf
from MyMods.ERP import SimpleParams as smp
# from MyMods.ERP import AnalysePack as ap
from MyMods.ERP import SeleniumPack as sp

url = "https://rasp.dmami.ru/"
rasp_html_path = "Расписания/html/"
rasp_json_path = "Расписания/json/"
#group = "201-341"



months ={"Янв": 1, "Фев": 2, "Мар": 3, "Апр": 4, "Май": 5, "Июн": 6, "Июл": 7, "Авг": 8, "Сен": 9, "Окт": 10, "Ноя": 11, "Дек": 12}



def find_groop(group):
    file_name = rasp_html_path+f"Расписание_для_{group}.html"
    try:
        browser, wwait = sp.start_FireFox(url)
        groops = wwait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div[1]/div[1]/div[3]/input")))
        groops.clear()
        groops.send_keys(group)
        gr_button = wwait.until(EC.presence_of_element_located((By.ID, group)))
        gr_button.click()
        week = wwait.until(EC.presence_of_element_located((By.CLASS_NAME, "schedule-week")))

        with open(file_name, "w", encoding="utf8") as file:
            file.write(week.get_attribute("innerHTML"))
            file.close()
    except Exception as ex:
        print(ex)
        pass
    finally:
        browser.close()
        browser.quit()
    return file_name

def get_all_rasp(group):
    fn_html = rasp_html_path+f"Расписание_для_{group}.html"
    fn_json = rasp_json_path+f"Расписание_для_{group}.json"
    if os.path.exists(fn_html):
        with open(fn_html, "r", encoding="utf8") as fp:
            src = fp.read()
            soup = bs(src, "html5lib")
            fp.close()

        days = soup.find_all("div", class_="schedule-day")
        less_all = {}
        l = 0
        for day in days:
            day_title = day.find("div", class_="schedule-day__title").text.strip()
            less_all.update({day_title : {}})
            pairs = day.find("div", class_="pairs").find_all("div", class_="pair")
            less_all[day_title].update({"id":l})
            l += 1
            k = 0
            for pair in pairs:
                lessons = pair.find("div", class_="lessons").find_all("div", class_="schedule-lesson")
                lesson_time = pair.find("div", class_="time").text.strip()
                for lesson in lessons:
                    lesson_cl = lesson.get_attribute_list("class")
                    if not 'schedule-day_old' in lesson_cl:
                        k = k + 1
                        lesson_name = lesson.find("div", class_="bold").text.strip()
                        lesson_small_name = lesson_name
                        lesson_link = lesson.find("div", class_="schedule-auditory").find("a")
                        auditorium = lesson.find("div", class_="schedule-auditory").text.strip()
                        teacher = lesson.find("div", class_="teacher").text.strip()
                        lesson_start_end_date = lesson.find("div", class_="schedule-dates").text.strip()
                        date_fp = lesson_start_end_date.split(" ")
                        today_date = date.today()
                        min_date = date(today_date.year, months[date_fp[1]], int(date_fp[0]))
                        max_date = date(today_date.year, months[date_fp[4]], int(date_fp[3]))
                        print(day_title, ":", min_date, "|", max_date, "|", today_date)

                        if (today_date >= min_date) and (today_date <= max_date):
                            if len(lesson_small_name)>39:
                                lesson_small_name = lesson_small_name[:lesson_name.find("(")].strip()
                                if len(lesson_small_name)>39:
                                    lesson_small_name = lesson_small_name[:39].strip()
                            less_all[day_title].update(
                                {
                                    f"tim_{k}": lesson_time,
                                    f"les_{k}" : lesson_name,
                                    f"les_sm_{k}" : lesson_small_name,
                                    f"prep_{k}" : teacher,
                                }
                            )

                            if lesson_link == None:
                                less_all[day_title].update({f"aud_{k}": auditorium})
                            else:
                                less_all[day_title].update(
                                    {
                                        f"aud_{k}": auditorium,
                                        f"lin_{k}": lesson_link.get("href")
                                    }
                                )
                            less_all[day_title].update({f"date_{k}":lesson_start_end_date})
            less_all[day_title].update({"les_have":k})

        data = json.dumps(less_all, indent=2, ensure_ascii=False)
        with open(fn_json, "w", encoding="utf8") as file:
            file.write(data)
            file.close()
        print("json сохранен")
        return fn_json
    else:
        find_groop(group)
        get_all_rasp(group)

# ------------------------------------------------------------------------------

user_path = "Пользователи/"


def make_log_json(message, id, messenger):
    text = message
    print(text)
    group = ""
    autonotification = ""

    try:
        with open(user_path+messenger+"/"+f"{id}.json", "r", encoding="utf8") as file:
            dd = json.load(file)
            file.close()
        print(id, dd)
        group = dd["group"]
        autonotification = dd["autonotification"]
    except:
        print("No user")

    if autonotification == "":
        autonotification = "нет"

    try:
        text = text.casefold().split(" ")
        print(text)
        if "группа:" in text:
            group = text[text.index("группа:")+1]
        elif len(text[0].split("-"))==2:
            group = text[0]
        if "авторассылка:" in text:
            autonotification = text[text.index("авторассылка:")+1]


        with open(user_path+messenger+"/"+f"{id}.json", "w", encoding="utf8") as file:
            file.write(json.dumps({'group': group, 'autonotification': autonotification}, ensure_ascii=False, indent=4))
        return "Данные успешно обновлены"
    except Exception as e:
        return "Возникла непредвиденная ошибка: " + str(e)


def make_log(message, id, messenger):
    text = message
    print(text)
    group = ""
    autonotification = ""

    try:
        with open(user_path+messenger+"/"+f"{id}.txt", "r", encoding="utf8") as file:
            dd = file.read()
            file.close()
        print(id, dd)
        dd = dd.casefold().split(" ")
        if "группа:" in dd:
            group = dd[dd.index("группа:")+1]
        if "авторассылка:" in dd:
            autonotification = dd[dd.index("авторассылка:")+1]
    except:
        print("No user")

    if autonotification == "":
        autonotification = "нет"

    try:
        text = text.casefold().split(" ")
        print(text)
        if "группа:" in text:
            group = text[text.index("группа:")+1]
            print("1")
        print("Group")
        if "авторассылка:" in text:
            autonotification = text[text.index("авторассылка:")+1]
            print("2")
        print("Aut")
        with open(user_path+f"{id}.txt", "w", encoding="utf8") as file:
            file.write(f"Группа: {group} Авторассылка: {autonotification}")
            file.close()
            print("3")
        return "Данные успешно обновлены"
    except:
        return "Возникла непредвиденная ошибка"

def get_json_schedule(group):
    try:
        with open(rasp_json_path+f"Расписание_для_{group}.json", "r", encoding='utf-8') as file:
            data = json.load(file)
            file.close()
        return data
    except:
        get_all_rasp(group)
        return get_json_schedule(group)

def get_log_json(id, messenger):
    try:
        with open(user_path+messenger+"/"+f"{id}.json", "r", encoding="utf8") as file:
            dd = json.load(file)
            file.close()
        print(id, dd)
        group = dd["group"]
        autonotification = dd["autonotification"]
        return (group, autonotification)
    except:
        raise Exception("Логи не заданы!")


def get_log(id):
    try:
        with open(user_path+f"{id}.txt", "r", encoding="utf8") as file:
            dd = file.read()
            file.close()
        dd = dd.split(" ")
        group = ""
        autonotification = ""
        if "Группа:" in dd:
            try:
                group = dd[1]
            except:
                group = ""
        if "Авторассылка:" in dd:
            try:
                autonotification = dd[3]
            except:
                autonotification = ""
        if group is not None and autonotification is not None:
            return (group, autonotification)
    except:
        raise Exception("Вы не задали логи")

def day_schedule(day, id, messanger):
    print(id)
    group, autonotification = get_log_json(id, messanger)

    data = get_json_schedule(group)
    schedule = data[day.title()]
    answer_text = day.title()
    lesson_time = None
    lesson_name = None
    lesson_small_name = None
    auditorium = None
    lesson_link = None
    teacher = None
    lesson_start_end_date = None
    links = []
    if schedule["les_have"] > 0:
        for i in range(1, schedule["les_have"]+1):
            auditorium = None
            lesson_link = None
            try:
                i = str(i)
                if schedule["les_" + i] != None:
                    lesson_time = schedule["tim_" + i]
                    lesson_name = schedule["les_" + i]
                    lesson_small_name = schedule["les_sm_" + i]
                    lesson_start_end_date = schedule["date_" + i]
                    try:
                        auditorium = schedule["aud_" + i]
                    except:
                        pass
                    try:
                        lesson_link = schedule["lin_" + i]
                    except:
                        pass
                    teacher = schedule["prep_" + i]
                    answer_text = answer_text + f'\n\n{lesson_time}'
                    answer_text = answer_text + f'\n{lesson_name}'
                    answer_text = answer_text + f'\n{teacher}'
                    if auditorium != None:
                        answer_text = answer_text + f'\nПроходит в {auditorium}'
                    if lesson_link != None:
                        links.append([lesson_small_name, lesson_link])
                    answer_text = answer_text + f'\n{lesson_start_end_date}'
            except:
                pass
    elif schedule["les_have"] == 0:
        answer_text = answer_text + f'\n\nВ этот день пар нет\n'
    keyboard = links
    answer_text = answer_text + f'\n{datetime.now().strftime("%A, %d. %B %Y %I:%M%p")}'
    return [answer_text, keyboard]


def now_schedule(id, messanger):
    group, autonotification = get_log_json(id, messanger)
    data = get_json_schedule(group)
    answer_text = ""
    link = ""
    links = []
    for d in data:
        if data[d]["id"] == datetime.today().weekday():
        # if data[d]["id"] == 1:
            if data[d]["les_have"]:
                for i in range(data[d]["les_have"]):
                    try:
                        i = str(i+1)
                        lesson_time = data[d]["tim_" + i]
                        if len(lesson_time[:lesson_time.find("-")])<5:
                            lesson_time = "0" + lesson_time
                        min_time = time.fromisoformat(lesson_time[:lesson_time.find("-")])
                        if len(lesson_time[lesson_time.find("-")+1:])<5:
                            lesson_time = lesson_time[:lesson_time.find("-")] + "0" + lesson_time[lesson_time.find("-")+1:]
                        max_time = time.fromisoformat(lesson_time[lesson_time.find("-")+1:])
                        time_now = datetime.today().time()
                        # time_now = time(hour=11)
                        #time_now = time(12,21)
                        if time_now >= min_time and time_now <= max_time:
                            answer_text += "Сейчас идет: " + data[d]["les_" + i] + f"\n"
                            answer_text += "Преподаватель: " + data[d]["prep_" + i] + f"\n"
                            try:
                                answer_text += "Проходит в: " + data[d]["aud_" + i] + f"\n"
                            except:
                                pass
                            try:
                                link = data[d]["lin_" + i]
                                sn = data[d]["les_sm_" + i]
                                links = [[sn, link]]
                            except:
                                pass
                            return [answer_text, links]

                    except:
                        raise Exception("Сегодняшнее расписание")

    answer_text = "Сейчас нет пар"
    return [answer_text, links]



def test(id):
    try:
        print("1")
        with open(user_path+f"{id}.txt", "r", encoding="utf8") as file:
            dd = file.read()
            file.close()
        print(dd)
        dd = dd.split(" ")
        if "Группа:" in dd:
            print(dd[1])
    except:
        with open(user_path+f"{id}.txt", "w", encoding="utf8") as file:
            file.write("Группа: 201-341")
            file.close()
        test(id)

# ------------------------------------------------------------------------------


if __name__=="__main__":
    group = "201-363"
    # find_groop(group)
    # get_all_rasp(group)
    # print(make_log_json("Группа: 201-341", 1))
    # print(get_log_json(1))
    # print(day_schedule("Суббота", 1))
    print(now_schedule(1))
