import requests
from time import sleep
from bs4 import BeautifulSoup

request_interval = 3600  # seconds
url1 = "https://api.session-search.prod.ielts.com/v2/sessions/search"
url2 = "https://irsafam.org/ielts/timetable?city%5B%5D=tehran&model%5B%5D=cdielts&month%5B%5D=08"
payload = {
    "dayOfPaperTest": 0,
    "languageSkills": ["L", "R", "W"],
    "order": "A",
    "page": 1,
    "pageSize": 100,
    "sortBy": "TEST_START_DATE",
    "timesOfDay": ["MORNING", "AFTERNOON"],
    "fromTestStartDateLocal": "2025-06-30",
    "toTestStartDateLocal": "2025-11-29",
    "countryCode": "IRN",
    "city": "Tehran",
    "testDeliveryFormats": ["CD"],
    "testCategories": ["IELTS"],
    "testModules": ["ACADEMIC"],
}


def fetch_available_sessions():
    try:
        response = requests.post(url1, json=payload)
        response.raise_for_status()
        data = response.json()
        sessions = data.get("items", [])
        return sessions
    except:
        raise Exception(f"Error fetching data: {response.status_code}")


def fetch_available_sessions_from_irsafam():
    try:
        response = requests.get(url2)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        main_element = soup.find("main")
        msg = ""
        if main_element:
            main_text = main_element.get_text(strip=True)
            if (
                "بر اساس جستجوی شما هیچ آزمونی پیدا نشد. لطفا جستجوی انجام شده خود را اصلاح نمایید."
                in main_text
            ):
                msg += "\nNo sessions found in IRSAFAM HTML response."
            else:
                msg += "\nSomething's Up!!!!"
        else:
            msg += "\nNo <main> element found in HTML response."
        return msg
    except Exception as e:
        raise Exception(
            f"Error fetching data from irsafam: {response.status_code} \n {e}"
        )


def prepare_msg_from_sessions(sessions):
    line = "---------------------------\n"
    msg = line
    for s in sessions:
        seat_info = s.get("seatAvailability", {})
        max_avail_seats = seat_info.get("maxAvailable", None)
        remaining_seats = seat_info.get("remaining", None)
        start_date_iso = s.get("testStartLocalDatetime", None)
        start_date = (
            start_date_iso.split("T")[0]
            if start_date_iso is not None
            else "UNKNOWN_DATE"
        )
        msg += f"🕒{start_date} | 💠 Max: {max_avail_seats} | ✅ Remaining: {remaining_seats}\n"
        msg += line

    return msg


def notify_user(msg):
    bot_msg_url = "https://api.telegram.org/bot7981904895:AAE2Y0Ylk7MuK4wsg4ePAYl-A6TTQQzqeKU/sendMessage"
    chat_id = 108630953
    print(f"\n\n{msg}")
    print("Sending msg to telegram...")
    requests.post(
        bot_msg_url,
        json={
            "chat_id": chat_id,
            "text": msg,
            "parse_mode": "Markdown",
        },
    )


def main():
    while True:
        msg1 = ""
        msg2 = ""
        try:
            sessions = fetch_available_sessions()
            msg1 = prepare_msg_from_sessions(sessions)
            msg2 = fetch_available_sessions_from_irsafam()
        except Exception as e:
            msg1 = str(e)
        finally:
            notify_user(msg1)
            notify_user(msg2)
            sleep(request_interval)


if __name__ == "__main__":
    main()
