import json
import urllib3


# Twilio config
TWIL_SID = ""
TWIL_TOKEN = ""
TWIL_TO = "5555555555"  # Number to send SMS to
TWIL_FROM = "+15555555555"  # Your 'from' number
TWIL_ENDPOINT = f"https://api.twilio.com/2010-04-01/Accounts/{TWIL_SID}/Messages.json"
TWIL_HEADERS = urllib3.make_headers(basic_auth=f"{TWIL_SID}:{TWIL_TOKEN}")

# Resy config
RESY_ENDPOINT = "https://api.resy.com/4/find"
RESY_HEADERS = {"Authorization": 'ResyAPI api_key=""'}  # Pull from devtools
RESY_VENUE = 1263
RESY_PARTY_SIZE = 2

# Extra data to include in message - for example, link to reservation page
EXTRA_DATA = ""

# Days to check for slots
VALID_DAYS = [
    "2023-03-27",
    "2023-03-28",
    "2023-03-29",
    "2023-03-30",
    "2023-03-31",
    "2023-04-01",
    "2023-04-02",
]

http = urllib3.PoolManager()


def send_text(available):
    texts = []
    for date, times in available:
        times_text = ", ".join(times[:3])
        texts.append(f"{date}: {times_text}")

    if EXTRA_DATA:
        texts.append(EXTRA_DATA)

    msg = "\n".join(texts)
    http.request(
        "POST",
        TWIL_ENDPOINT,
        fields={"From": TWIL_FROM, "To": TWIL_TO, "Body": msg},
        headers=TWIL_HEADERS,
    )


def lambda_handler(*_):
    available = []

    for DAY in VALID_DAYS:
        response = http.request(
            "GET",
            RESY_ENDPOINT,
            headers=RESY_HEADERS,
            fields={
                "lat": 0,
                "long": 0,
                "day": DAY,
                "party_size": RESY_PARTY_SIZE,
                "venue_id": RESY_VENUE,
            },
        )

        data = json.loads(response.data)

        if venues := data["results"]["venues"]:
            if slots := venues[0]["slots"]:
                times = set()
                for slot in slots:
                    start_datetime = slot["date"]["start"]
                    start_time = start_datetime.split(" ")[-1]
                    start_time_nosec = start_time.rsplit(":", 1)[0]
                    times.add(start_time_nosec)

                available.append((DAY, sorted(times)))
        else:
            print("No venue found")
            return

    if available:
        for day, hours in available:
            print(f"found slots on {day}: {hours}")

        send_text(available)
    else:
        print("no slots found")


lambda_handler({}, {}) if __name__ == "__main__" else None
