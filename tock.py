import json
import urllib3


# Twilio config
TWIL_SID = ""
TWIL_TOKEN = ""
TWIL_TO = "5555555555"  # Number to send SMS to
TWIL_FROM = "+15555555555"  # Your 'from' number
TWIL_ENDPOINT = f"https://api.twilio.com/2010-04-01/Accounts/{TWIL_SID}/Messages.json"
TWIL_HEADERS = urllib3.make_headers(basic_auth=f"{TWIL_SID}:{TWIL_TOKEN}")

TOCK_ENDPOINT = "https://www.exploretock.com/api/consumer/calendar/full"
TOCK_HEADERS = {
    "x-tock-path": "/perse/", # pull these from devtools
    "x-tock-scope": '{"businessId":696,"businessGroupId":"478","site":"EXPLORETOCK"}',
}
TOCK_MIN_SEATS = 2

# URL to include in SMS - set to reservation page link
SMS_URL = "https://bit.ly/..."

# Days to check for slots
VALID_DAYS = [
    "2022-08-26",
    "2022-08-27",
    "2022-08-28",
    "2022-08-29",
    "2022-08-30",
    "2022-08-31",
    "2022-09-01",
]

http = urllib3.PoolManager()


def send_text(available):
    texts = []
    for date, time in available:
        texts.append(f"{date}: {time}")

    texts.append(SMS_URL)

    http.request(
        "POST",
        TWIL_ENDPOINT,
        fields={"From": TWIL_FROM, "To": TWIL_TO, "Body": "\n".join(texts)},
        headers=TWIL_HEADERS,
    )


def lambda_handler(event, _):
    response = http.request("POST", TOCK_ENDPOINT, body="{}", headers=TOCK_HEADERS)
    data = json.loads(response.data)

    available = []
    for res in data["result"]["ticketGroup"]:
        if res["date"] not in VALID_DAYS:
            continue
        if res["minPurchaseSize"] > TOCK_MIN_SEATS:
            continue
        if not res["availableTickets"]:
            continue
        if res["isCommunal"]:
            continue
        available.append((res["date"], res["time"]))

    print(f"found {len(available)} matching reservations")
    if available:
        send_text(available)


lambda_handler({}, {}) if __name__ == "__main__" else None
