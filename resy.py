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

# URL to include in SMS - set to reservation page link
SMS_URL = "https://bit.ly/..."

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
    for date, count in available:
        texts.append(f"{date}: {count}")

    texts.append(SMS_URL)

    http.request(
        "POST",
        TWIL_ENDPOINT,
        fields={"From": TWIL_FROM, "To": TWIL_TO, "Body": "\n".join(texts)},
        headers=TWIL_HEADERS,
    )


def lambda_handler(*args):
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

        if slots := data["results"]["venues"][0]["slots"]:
            available.append((DAY, len(slots)))

    print(f"found {len(available)} days with slots")
    if available:
        send_text(available)


lambda_handler({}, {}) if __name__ == "__main__" else None
