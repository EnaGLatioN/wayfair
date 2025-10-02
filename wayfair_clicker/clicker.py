from email.policy import default

import requests
import json
import time
import random
import argparse
from decouple import config as cnf
from datetime import datetime, timedelta
from logger import setup_logger

logger = setup_logger()
RESPONSE_FILE = "wayfair_responses.json"
IDS = []


def get_job_payload():
    time_delta = cnf("TIME_DELTA", cast=int, default=5)
    target_date = datetime.now() + timedelta(hours=time_delta)
    formatted_date = target_date.strftime("%Y-%m-%d")
    return {
        "hash": cnf("HASH_GET_AVAIL_JOBS", cast=str, default="23652345kjkghjgjhk234jh5hj"),
        "variables": {
            "startDate": formatted_date
        }
    }

def get_details_payload(round_job_id):
    return {
        "hash": cnf("HASH_DETAILS_JOB", cast=str, default="87kdgfhlsdfg9f9gsf88ffsfg"),
        "variables": {
            "proJobRoundID": round_job_id
        }
    }


def get_claim_payload(round_job_id, job_date):
    return {
        "hash": cnf("HASH_ClAIM_JOB", cast=str, default="90adsvcatv77zdsfg798asdf09"),
        "variables": {
            "date": job_date,
            "proJobRoundID": round_job_id
        }
    }


def get_headers():
    return {
        "X-PX-OS-VERSION": f"{cnf('X-PX-OS-VERSION', cast=str, default='18.6.2')}",
        "Accept-Language": f"{cnf('ACCEPT-LANGUAGE', cast=str, default='ru')}",
        "X-PX-VID": f"{cnf('X-PX-VID', cast=str, default='61dcee5d-a14b-11f0-a7ad-7b2c41dbf4aa')}",
        "Connection": f"{cnf('CONNECTION', cast=str, default='keep-alive')}",
        "Accept": f"{cnf('ACCEPT', cast=str, default='application/json')}",
        "X-PX-DEVICE-FP": f"{cnf('X-PX-DEVICE-FP', cast=str, default='DD6382DE-FC6A-4B59-B94E-F18334B1A71D')}",
        "wf-customer-guid": f"{cnf('WF-CUSTOMER-GUID', cast=str, default='AC84D264-98B4-4816-B77A-0E846B95E5EE')}",
        "X-PX-HELLO": f"{cnf('X-PX-HELLO', cast=str, default='C1UKBwABVwEeUgoLAh4CAlUDHlIHBVIeVwQLUgUEA1VQVQZW')}",
        "wf-pageview-id": f"{cnf('WF-PAGEVIEW-ID', cast=str, default='UkRVMlJrRXdOVGd0UkVNeA==')}",
        "X-PX-MOBILE-SDK-VERSION": f"{cnf('X-PX-MOBILE-SDK-VERSION', cast=str, default='3.2.5')}",
        "X-Graph-Type": f"{cnf('X-GRAPH-TYPE', cast=str, default='3')}",
        "Content-Type": f"{cnf('CONTENT-TYPE', cast=str, default='application/json')}",
        "X-PX-AUTHORIZATION": f"{cnf('X-PX-AUTHORIZATION', cast=str, default='3:3bdf1ec904b8f5ce02275e4441742f00621e4330666b2c3a0adb9fab8c5cff89:amc2H9cc+AhUDt33ScnweGVOv+2p0QNNF3jPcS+h0agyKuLcgDp4IsNF9qlExvIdeB2Z0aB9H10dhfINDS/1hg==:1000:66erc2ygX6DZEQ5FQPFTIJ4PiwV4Vv3rqM3wE7MKw8HRVYpsiQc5ENFqUNmiLurrkauyxXuUdsqSkXtUObcQN/T4N+kDSXGtt4K9oRcFLMlVy4HLLJaUd8Iaiz1vEjSwKVoe9hziiV8nKWUouKsz72lc4pifp+eM83Xq+ReZdtkOH/2jhON/ccQoYRTbAzaPrJGloKYi+y/gUVQdB127puOx3oOyMNzr9BPFOU/lFiM=')}",
        "User-Agent": f"{cnf('USER-AGENT', cast=str, default='WayhomeApp/20250910.12080 1.100.0 (iPhone; iOS 18.6.2; Scale/3.00)')}",
        "wf-locale": f"{cnf('WF-LOCALE', cast=str, default='en-US')}",
        "X-PX-UUID": f"{cnf('X-PX-UUID', cast=str, default='8f9432d2-a981-11f0-a46a-d78a670fcf5e')}",
        "AppAuthEnabled": f"{cnf('APP_AUTH_ENABLED', cast=str, default='1')}",
        "Authorization": f"{cnf('AUTHORIZATION', cast=str, default='Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6InBlRG5BMWVVVGRVQU00YVdjU3FnZm40ZEJhbFZCYnJ4R2ZEU0ZQYXVQbG8iLCJ4NXQiOiJxQndkQ25kdEhGZC14dHgzUGY2dnVQMkhWMkEiLCJ0eXAiOiJKV1QiLCJqa3UiOiJodHRwczovL3Nzby5hdXRoLndheWZhaXIuY29tLy53ZWxsLWtub3duL29wZW5pZC1jb25maWd1cmF0aW9uL2p3a3MifQ.eyJuYmYiOjE3NjA0NDI1NjAsImV4cCI6MTgyMzUxNDU2MSwiaWF0IjoxNzYwNDQyNTYxLCJpc3MiOiJodHRwczovL3Nzby5hdXRoLndheWZhaXIuY29tLyIsImF1ZCI6ImF1dGhfaWRlbnRpdHkiLCJjbGllbnRfaWQiOiJ5NnZVV0dUd2dFVlA0VEFZbXZuTGxBIiwiY3VpZCI6IjYxMzU5NDYwODYiLCJzdWIiOiIzMDg3NDI0NjMiLCJwbHQiOiJ1bmtub3duIiwib3JpZ2luYWxfaWF0IjoiMTc1OTYwMDI0MiIsInJvbGUiOiJzZjpjdXN0b21lciIsInZlcnNpb24iOiIxLjAiLCJqdGkiOiIzQ0FCRDdCMzc4NzFBMzUxQTZBODQ4N0M2OTAwRDRCRCIsInNjb3BlIjoib3BlbmlkIHNmOnJlY29nbml6ZWQgc2Y6dHJ1c3RlZCBzZjp2ZXJpZmllZCIsImFtciI6WyJwZXJzaXN0ZW5jZSIsInBhc3N3b3JkIl19.OIAd7nb0MsEerGQaqdUFQeMbrHL057GGypIYQsyaskH7pFrZ8qSCVYuOu2o5zGdUjeSdQITfb-3_9O3Olps-BXOYeIlwDcEWmQBL9nEuLRz899t-oaTR-TRCvp8tEVXcNgVeZcZrMl08T-mfC7PoLkPG5GFR_dupT1y7-kMz-LjiLGAS2lpQbiehPKxdQrAEpAqA-Bj9Yxt0sfaR5YGnZ_yc7DIQ7_WPnlnDf4pVjQi-kcKHBggP1ZyhJfzU7fjSwjwBfFguOJFJi_Cto_1LmpOIfhQTryE1eNuEKQyiiutNpm-duQTFG2he0hiJCnr-5hodRLRRkQrzl_3ws83hYW12wvvHppsMmnvVoyZPiKLEgvexA-r2Pt0fLGN_irVaE5yrdxAPkS8xE5NAUJBhBNsXe7wrCXa1kV5YKUD0QUKBIiKPyp6R08sWq_X9yaZPgM7Zf2X0JUzzV46E35MTkG2UJhRWYhotd1nhRVfHcO3Zl3pXsIbyRU68nQTPtGrin3ZwR71G8MOUqwYQpS_plau7y4Smr-o5npXxp3-hwOyW7uzoBXaogtFudNbI3-XZ1Il4DY7KFbsgFibL227T0kT0GgaTJZFkXcO1vBLhOzsRTmzW7_C81JCxYhJizQvGpdE5qvDwpGTFAI0V9Aym0iwQHo0ntwB5uRMC_XlTTmU')}",
        "Accept-Encoding": f"{cnf('ACCEPT-ENCODING', cast=str, default='gzip, deflate, br')}",
        "X-PX-DEVICE-MODEL": f"{cnf('X-PX-DEVICE-MODEL', cast=str, default='iPhone15,5')}",
        "wf-device-guid": f"{cnf('WF-DEVICE-GUID', cast=str, default='39B9B4BC-BAC5-4DD7-8412-0637CE162DB6')}",
        "Host": f"{cnf('HOST', cast=str, default='www.wayfair.com')}",
        "Cookie": f"{cnf('COOKIE', cast=str, default='SFSID=c6e23398196bee2c18a3cf68774e3ad2; canary=0; i18nPrefs=lang%3Den-US; postalCode=91405; serverUAInfo=%7B%22browser%22%3A%22WayhomeAppIos%22%2C%22browserVersion%22%3A%22%22%2C%22OS%22%3A%22iOS%22%2C%22OSVersion%22%3A18.62%2C%22isMobile%22%3Atrue%2C%22isTablet%22%3Afalse%2C%22isTouch%22%3Afalse%7D; vid=c1bfcebc-e7ec-4198-a2d4-f771005dc98b; WFDC=PDX; CSN_CSRF=15dddd75a02f712948d7daf3833f2c34cdea7feef0487dc0e99dfdfa3f32917a; CSN_CT=eyJhbGciOiJSUzI1NiIsImtpZCI6InBlRG5BMWVVVGRVQU00YVdjU3FnZm40ZEJhbFZCYnJ4R2ZEU0ZQYXVQbG8iLCJ4NXQiOiJxQndkQ25kdEhGZC14dHgzUGY2dnVQMkhWMkEiLCJ0eXAiOiJKV1QiLCJqa3UiOiJodHRwczovL3Nzby5hdXRoLndheWZhaXIuY29tLy53ZWxsLWtub3duL29wZW5pZC1jb25maWd1cmF0aW9uL2p3a3MifQ.eyJuYmYiOjE3NjA0NDI1NjAsImV4cCI6MTgyMzUxNDU2MSwiaWF0IjoxNzYwNDQyNTYxLCJpc3MiOiJodHRwczovL3Nzby5hdXRoLndheWZhaXIuY29tLyIsImF1ZCI6ImF1dGhfaWRlbnRpdHkiLCJjbGllbnRfaWQiOiJ5NnZVV0dUd2dFVlA0VEFZbXZuTGxBIiwiY3VpZCI6IjYxMzU5NDYwODYiLCJzdWIiOiIzMDg3NDI0NjMiLCJwbHQiOiJ1bmtub3duIiwib3JpZ2luYWxfaWF0IjoiMTc1OTYwMDI0MiIsInJvbGUiOiJzZjpjdXN0b21lciIsInZlcnNpb24iOiIxLjAiLCJqdGkiOiIzQ0FCRDdCMzc4NzFBMzUxQTZBODQ4N0M2OTAwRDRCRCIsInNjb3BlIjoib3BlbmlkIHNmOnJlY29nbml6ZWQgc2Y6dHJ1c3RlZCBsZjp2ZXJpZmllZCIsImFtciI6WyJwZXJzaXN0ZW5jZSIsInBhc3N3b3JkIl19.OIAd7nb0MsEerGQaqdUFQeMbrHL057GGypIYQsyaskH7pFrZ8qSCVYuOu2o5zGdUjeSdQITfb-3_9O3Olps-BXOYeIlwDcEWmQBL9nEuLRz899t-oaTR-TRCvp8tEVXcNgVeZcZrMl08T-mfC7PoLkPG5GFR_dupT1y7-kMz-LjiLGAS2lpQbiehPKxdQrAEpAqA-Bj9Yxt0sfaR5YGnZ_yc7DIQ7_WPnlnDf4pVjQi-kcKHBggP1ZyhJfzU7fjSwjwBfFguOJFJi_Cto_1LmpOIfhQTryE1eNuEKQyiiutNpm-duQTFG2he0hiJCnr-5hodRLRRkQrzl_3ws83hYW12wvvHppsMmnvVoyZPiKLEgvexA-r2Pt0fLGN_irVaE5yrdxAPkS8xE5NAUJBhBNsXe7wrCXa1kV5YKUD0QUKBIiKPyp6R08sWq_X9yaZPgM7Zf2X0JUzzV46E35MTkG2UJhRWYhotd1nhRVfHcO3Zl3pXsIbyRU68nQTPtGrin3ZwR71G8MOUqwYQpS_plau7y4Smr-o5npXxp3-hwOyW7uzoBXaogtFudNbI3-XZ1Il4DY7KFbsgFibL227T0kT0GgaTJZFkXcO1vBLhOzsRTmzW7_C81JCxYhJizQvGpdE5qvDwpGTFAI0V9Aym0iwQHo0ntwB5uRMC_XlTTmU; CSNID=AC84D264-98B4-4816-B77A-0E846B95E5EE; CSNBrief=DRF%3Ddsm1; WFCS=CS6; CSNUtId=2e955598-5ec1-4bcf-8995-ae71f81ee5d4; ExCSNUtId=39B9B4BC-BAC5-4DD7-8412-0637CE162DB6')}",
        "X-PX-OS": f"{cnf('X-PX-OS', cast=str, default='iOS')}"
    }


def get_job_details_request(round_job_id, chat_id):
    url = cnf("URL_DETAILS", cast=str, default="https://www.wayfair.com/dfghhdfghsg87hs7df7gsdf")

    try:
        response = requests.post(
            url,
            json=get_details_payload(round_job_id),
            headers=get_headers(),
            timeout=5
        )

        logger.info(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            resp = response.json()
            data = resp.get("data", None)
            pro = data.get("pro", None)
            pro_job = pro.get("proJobRoundConnection", None)
            edges = pro_job.get("edges", None)
            logger.info(f"+++++++++++++++++++get_job_details_request++++++++++++++++++++++++++")
            if edges:
                for edge in edges:
                    pro_job_round = edge.get("proJobRound", {})
                    job_round = pro_job_round.get("jobRound", {})
                    date_service = job_round.get("desiredServiceDate", None)
                    time_window = job_round.get("timeWindow", {})
                    start_times = time_window.get("startTimes", [])
                    if date_service and start_times:
                        random_time = random.choice(start_times)
                        result_string = f"{date_service} {random_time}.0000-0700"
                        logger.info(f"DATA service: {data}")
                        claim_job(round_job_id, result_string, chat_id)
            else:
                logger.info(f"No edges - {edges}")
        else:
            logger.info(f"\nError Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        logger.info(f"get_job_details_request - Request failed: {e}")
        return None


def make_wayfair_request(chat_id):
    url = cnf("URL_WF", cast=str, default="https://www.wayfair.com/wayhome/graphql?queasdfgbsdfgsdfgsdfgsdfg")
    while True:
        try:
            current_utc = datetime.utcnow()
            current_hour = current_utc.hour
            # Проверяем, нужно ли спать (с 5:00 до 13:00 UTC)
            if not (cnf("TIME_ONE", cast=int, default=5) <= current_hour < cnf("TIME_TWO", cast=int, default=13)):
                delay = random.uniform(0, 1)
                logger.info(f"Waiting {delay:.2f} seconds before request...")
                time.sleep(delay)
                response = requests.post(
                    url,
                    json=get_job_payload(),
                    headers=get_headers(),
                    timeout=7
                )
                logger.info(f"Status Code: {response.status_code}")
                if response.status_code == 200:
                    resp = response.json()
                    data = resp.get("data", None)
                    pro = data.get("pro", None)
                    pro_job = pro.get("proJobRoundConnection", None)
                    edges = pro_job.get("edges", None)
                    logger.info(data)
                    if edges:
                        for edge in edges:
                            pro_job = edge.get("proJobRound", None)
                            job_id = pro_job.get("id")
                            if job_id:
                                amaunt_flag = take_amaunt(pro_job)
                                if amaunt_flag:
                                    get_job_details_request(job_id, chat_id)
                                else:
                                    continue
                            else:
                                logger.info(f"No job_id - {job_id}")
                    else:
                        logger.info(f"No edges - {edges}")
                else:
                    logger.info(f"\nError Response: {response.text}")

        except requests.exceptions.RequestException as e:
            logger.info(f"make_wayfair_request - Request failed: {e}")
            time.sleep(30)
            continue


def take_amaunt(job_id):
    try:
        payments = job_id.get("payments", None)
        for payment in payments:
            amaunt = payment.get("total", None)
            if amaunt and (amaunt >= cnf("NEEDED_PRICE", cast=int, default=82)):
                return True
        return False
    except Exception as e:
        logger.error(f"take_amaunt - {e}")
        return False


def claim_job(round_job_id, job_date, chat_id):
    url = cnf("URL_CLAIM", cast=str, default="https://www.wayfair.com/wayhome/graphql?657dadfsfdgh87sgdhbsdfgsdfgsdfg")

    try:
        response = requests.post(
            url,
            json=get_claim_payload(round_job_id, job_date),
            headers=get_headers(),
            timeout=7
        )

        logger.info(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            resp = response.json()
            logger.info(f"1111Status Code: {resp}")
            if errors := resp.get("errors", None):
                for error in errors:
                    if mess := error.get('message', None):
                        send_telegram_message(
                            message=f"{mess} - {round_job_id} --- \n {resp}",
                            chat_id=chat_id
                        )
            else:
                data = resp.get("data", None)
                pro = data.get("pro", None)
                pro_job = pro.get("proJobRoundMutation", None)
                job_change = pro_job.get("jobChange", None)
                status = job_change.get("status")
                if status == "CONFIRMED":
                    send_telegram_message(
                        message=f"Взят заказ с айди - {round_job_id} \n На дату - {job_date}",
                        chat_id=chat_id
                    )
                else:
                    logger.info(f"Fail status - {status}")

                logger.info("\nResponse JSON:")
                logger.info(json.dumps(response.json(), indent=2))
        else:
            logger.info(f"\nError Response: {response.text}")
    except requests.exceptions.RequestException as e:
        logger.info(f"claim_job - Request failed: {e}")


def send_telegram_message(message, chat_id):
    """Отправляет сообщение в чат тг"""

    try:
        payload = {
            'chat_id': int(chat_id),
            'text': message
        }
        response = requests.post(f'https://api.telegram.org/bot{cnf("TELE_TOKEN", cast=str, default="8407176850:AAF3qq3LQl2WR_cjOHmodOh9pKVvd2uFU_g")}/sendMessage', json=payload)
        if response.status_code != 200:
            logger.info(f"Ошибка отправки уведомления в чат {chat_id}: {response.text}")
        else:
            logger.info(f"Уведомление отправлено в чат {chat_id}")
    except Exception as e:
        logger.info(f"Ошибка в send_telegram_message: {str(e)}")


def main(args):
    logger.info(f"АРГУМЕНТЫ СТАРТА БОТА--{args}")
    make_wayfair_request(args.chat_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Description of your script.")
    parser.add_argument("--token", type=str, help="Токен.")
    parser.add_argument("--chat_id", type=str, help="Токен.")
    main(parser.parse_args())
