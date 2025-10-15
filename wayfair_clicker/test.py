import requests
import json
import time
import random
from datetime import datetime

# Константа для имени файла
RESPONSE_FILE = "wayfair_responses.json"


def make_wayfair_request():
    # Случайная задержка от 1 до 5 секунд
    delay = random.uniform(1, 5)
    print(f"Waiting {delay:.2f} seconds before request...")
    time.sleep(delay)

    url = "https://www.wayfair.com/wayhome/graphql?queryHash=7632b54fcfa7cd10bec94e6cda6236bf&queryName=GetAvailableJobs"

    # Тело запроса
    payload = {
        "hash": "7632b54fcfa7cd10bec94e6cda6236bf",
        "variables": {
            "startDate": "2025-10-15"
        }
    }

    # Заголовки
    headers = {
        "X-PX-OS-VERSION": "18.6.2",
        "Accept-Language": "ru",
        "X-PX-VID": "61dcee5d-a14b-11f0-a7ad-7b2c41dbf4aa",
        "Connection": "keep-alive",
        "Accept": "application/json",
        "X-PX-DEVICE-FP": "DD6382DE-FC6A-4B59-B94E-F18334B1A71D",
        "wf-customer-guid": "AC84D264-98B4-4816-B77A-0E846B95E5EE",
        "X-PX-HELLO": "C1UKBwABVwEeUgoLAh4CAlUDHlIHBVIeVwQLUgUEA1VQVQZW",
        "wf-pageview-id": "UkRVMlJrRXdOVGd0UkVNeA==",
        "X-PX-MOBILE-SDK-VERSION": "3.2.5",
        "X-Graph-Type": "3",
        "Content-Type": "application/json",
        "X-PX-AUTHORIZATION": "3:3bdf1ec904b8f5ce02275e4441742f00621e4330666b2c3a0adb9fab8c5cff89:amc2H9cc+AhUDt33ScnweGVOv+2p0QNNF3jPcS+h0agyKuLcgDp4IsNF9qlExvIdeB2Z0aB9H10dhfINDS/1hg==:1000:66erc2ygX6DZEQ5FQPFTIJ4PiwV4Vv3rqM3wE7MKw8HRVYpsiQc5ENFqUNmiLurrkauyxXuUdsqSkXtUObcQN/T4N+kDSXGtt4K9oRcFLMlVy4HLLJaUd8Iaiz1vEjSwKVoe9hziiV8nKWUouKsz72lc4pifp+eM83Xq+ReZdtkOH/2jhON/ccQoYRTbAzaPrJGloKYi+y/gUVQdB127puOx3oOyMNzr9BPFOU/lFiM=",
        "User-Agent": "WayhomeApp/20250910.12080 1.100.0 (iPhone; iOS 18.6.2; Scale/3.00)",
        "wf-locale": "en-US",
        "X-PX-UUID": "8f9432d2-a981-11f0-a46a-d78a670fcf5e",
        "AppAuthEnabled": "1",
        "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6InBlRG5BMWVVVGRVQU00YVdjU3FnZm40ZEJhbFZCYnJ4R2ZEU0ZQYXVQbG8iLCJ4NXQiOiJxQndkQ25kdEhGZC14dHgzUGY2dnVQMkhWMkEiLCJ0eXAiOiJKV1QiLCJqa3UiOiJodHRwczovL3Nzby5hdXRoLndheWZhaXIuY29tLy53ZWxsLWtub3duL29wZW5pZC1jb25maWd1cmF0aW9uL2p3a3MifQ.eyJuYmYiOjE3NjA0NDI1NjAsImV4cCI6MTgyMzUxNDU2MSwiaWF0IjoxNzYwNDQyNTYxLCJpc3MiOiJodHRwczovL3Nzby5hdXRoLndheWZhaXIuY29tLyIsImF1ZCI6ImF1dGhfaWRlbnRpdHkiLCJjbGllbnRfaWQiOiJ5NnZVV0dUd2dFVlA0VEFZbXZuTGxBIiwiY3VpZCI6IjYxMzU5NDYwODYiLCJzdWIiOiIzMDg3NDI0NjMiLCJwbHQiOiJ1bmtub3duIiwib3JpZ2luYWxfaWF0IjoiMTc1OTYwMDI0MiIsInJvbGUiOiJzZjpjdXN0b21lciIsInZlcnNpb24iOiIxLjAiLCJqdGkiOiIzQ0FCRDdCMzc4NzFBMzUxQTZBODQ4N0M2OTAwRDRCRCIsInNjb3BlIjoib3BlbmlkIHNmOnJlY29nbml6ZWQgc2Y6dHJ1c3RlZCBzZjp2ZXJpZmllZCIsImFtciI6WyJwZXJzaXN0ZW5jZSIsInBhc3N3b3JkIl19.OIAd7nb0MsEerGQaqdUFQeMbrHL057GGypIYQsyaskH7pFrZ8qSCVYuOu2o5zGdUjeSdQITfb-3_9O3Olps-BXOYeIlwDcEWmQBL9nEuLRz899t-oaTR-TRCvp8tEVXcNgVeZcZrMl08T-mfC7PoLkPG5GFR_dupT1y7-kMz-LjiLGAS2lpQbiehPKxdQrAEpAqA-Bj9Yxt0sfaR5YGnZ_yc7DIQ7_WPnlnDf4pVjQi-kcKHBggP1ZyhJfzU7fjSwjwBfFguOJFJi_Cto_1LmpOIfhQTryE1eNuEKQyiiutNpm-duQTFG2he0hiJCnr-5hodRLRRkQrzl_3ws83hYW12wvvHppsMmnvVoyZPiKLEgvexA-r2Pt0fLGN_irVaE5yrdxAPkS8xE5NAUJBhBNsXe7wrCXa1kV5YKUD0QUKBIiKPyp6R08sWq_X9yaZPgM7Zf2X0JUzzV46E35MTkG2UJhRWYhotd1nhRVfHcO3Zl3pXsIbyRU68nQTPtGrin3ZwR71G8MOUqwYQpS_plau7y4Smr-o5npXxp3-hwOyW7uzoBXaogtFudNbI3-XZ1Il4DY7KFbsgFibL227T0kT0GgaTJZFkXcO1vBLhOzsRTmzW7_C81JCxYhJizQvGpdE5qvDwpGTFAI0V9Aym0iwQHo0ntwB5uRMC_XlTTmU",
        "Accept-Encoding": "gzip, deflate, br",
        "X-PX-DEVICE-MODEL": "iPhone15,5",
        "wf-device-guid": "39B9B4BC-BAC5-4DD7-8412-0637CE162DB6",
        "Host": "www.wayfair.com",
        "Cookie": "SFSID=c6e23398196bee2c18a3cf68774e3ad2; canary=0; i18nPrefs=lang%3Den-US; postalCode=91405; serverUAInfo=%7B%22browser%22%3A%22WayhomeAppIos%22%2C%22browserVersion%22%3A%22%22%2C%22OS%22%3A%22iOS%22%2C%22OSVersion%22%3A18.62%2C%22isMobile%22%3Atrue%2C%22isTablet%22%3Afalse%2C%22isTouch%22%3Afalse%7D; vid=c1bfcebc-e7ec-4198-a2d4-f771005dc98b; WFDC=PDX; CSN_CSRF=15dddd75a02f712948d7daf3833f2c34cdea7feef0487dc0e99dfdfa3f32917a; CSN_CT=eyJhbGciOiJSUzI1NiIsImtpZCI6InBlRG5BMWVVVGRVQU00YVdjU3FnZm40ZEJhbFZCYnJ4R2ZEU0ZQYXVQbG8iLCJ4NXQiOiJxQndkQ25kdEhGZC14dHgzUGY2dnVQMkhWMkEiLCJ0eXAiOiJKV1QiLCJqa3UiOiJodHRwczovL3Nzby5hdXRoLndheWZhaXIuY29tLy53ZWxsLWtub3duL29wZW5pZC1jb25maWd1cmF0aW9uL2p3a3MifQ.eyJuYmYiOjE3NjA0NDI1NjAsImV4cCI6MTgyMzUxNDU2MSwiaWF0IjoxNzYwNDQyNTYxLCJpc3MiOiJodHRwczovL3Nzby5hdXRoLndheWZhaXIuY29tLyIsImF1ZCI6ImF1dGhfaWRlbnRpdHkiLCJjbGllbnRfaWQiOiJ5NnZVV0dUd2dFVlA0VEFZbXZuTGxBIiwiY3VpZCI6IjYxMzU5NDYwODYiLCJzdWIiOiIzMDg3NDI0NjMiLCJwbHQiOiJ1bmtub3duIiwib3JpZ2luYWxfaWF0IjoiMTc1OTYwMDI0MiIsInJvbGUiOiJzZjpjdXN0b21lciIsInZlcnNpb24iOiIxLjAiLCJqdGkiOiIzQ0FCRDdCMzc4NzFBMzUxQTZBODQ4N0M2OTAwRDRCRCIsInNjb3BlIjoib3BlbmlkIHNmOnJlY29nbml6ZWQgc2Y6dHJ1c3RlZCBsZjp2ZXJpZmllZCIsImFtciI6WyJwZXJzaXN0ZW5jZSIsInBhc3N3b3JkIl19.OIAd7nb0MsEerGQaqdUFQeMbrHL057GGypIYQsyaskH7pFrZ8qSCVYuOu2o5zGdUjeSdQITfb-3_9O3Olps-BXOYeIlwDcEWmQBL9nEuLRz899t-oaTR-TRCvp8tEVXcNgVeZcZrMl08T-mfC7PoLkPG5GFR_dupT1y7-kMz-LjiLGAS2lpQbiehPKxdQrAEpAqA-Bj9Yxt0sfaR5YGnZ_yc7DIQ7_WPnlnDf4pVjQi-kcKHBggP1ZyhJfzU7fjSwjwBfFguOJFJi_Cto_1LmpOIfhQTryE1eNuEKQyiiutNpm-duQTFG2he0hiJCnr-5hodRLRRkQrzl_3ws83hYW12wvvHppsMmnvVoyZPiKLEgvexA-r2Pt0fLGN_irVaE5yrdxAPkS8xE5NAUJBhBNsXe7wrCXa1kV5YKUD0QUKBIiKPyp6R08sWq_X9yaZPgM7Zf2X0JUzzV46E35MTkG2UJhRWYhotd1nhRVfHcO3Zl3pXsIbyRU68nQTPtGrin3ZwR71G8MOUqwYQpS_plau7y4Smr-o5npXxp3-hwOyW7uzoBXaogtFudNbI3-XZ1Il4DY7KFbsgFibL227T0kT0GgaTJZFkXcO1vBLhOzsRTmzW7_C81JCxYhJizQvGpdE5qvDwpGTFAI0V9Aym0iwQHo0ntwB5uRMC_XlTTmU; CSNID=AC84D264-98B4-4816-B77A-0E846B95E5EE; CSNBrief=DRF%3Ddsm1; WFCS=CS6; CSNUtId=2e955598-5ec1-4bcf-8995-ae71f81ee5d4; ExCSNUtId=39B9B4BC-BAC5-4DD7-8412-0637CE162DB6",
        "X-PX-OS": "iOS"
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30
        )

        print(f"Status Code: {response.status_code}")

        # Подготавливаем данные для сохранения
        response_data = {
            "timestamp": datetime.now().isoformat(),
            "delay_seconds": round(delay, 2),
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "response": response.json() if response.status_code == 200 else response.text
        }

        # Загружаем существующие данные или создаем новый список
        try:
            with open(RESPONSE_FILE, 'r', encoding='utf-8') as f:
                all_responses = json.load(f)
        except FileNotFoundError:
            all_responses = []

        # Добавляем новый ответ
        all_responses.append(response_data)

        # Сохраняем обновленные данные обратно в файл
        with open(RESPONSE_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_responses, f, indent=2, ensure_ascii=False)

        print(f"Response appended to: {RESPONSE_FILE}")
        print(f"Total responses in file: {len(all_responses)}")

        # Выводим информацию в консоль
        if response.status_code == 200:
            print("\nResponse JSON:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"\nError Response: {response.text}")

        return response

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

        # Сохраняем информацию об ошибке в тот же файл
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "delay_seconds": round(delay, 2),
            "error": str(e),
            "status_code": None
        }

        # Загружаем существующие данные или создаем новый список
        try:
            with open(RESPONSE_FILE, 'r', encoding='utf-8') as f:
                all_responses = json.load(f)
        except FileNotFoundError:
            all_responses = []

        # Добавляем информацию об ошибке
        all_responses.append(error_data)

        # Сохраняем обновленные данные
        with open(RESPONSE_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_responses, f, indent=2, ensure_ascii=False)

        print(f"Error appended to: {RESPONSE_FILE}")
        print(f"Total entries in file: {len(all_responses)}")

        return None


# Функция для просмотра сохраненных данных
def view_saved_responses():
    try:
        with open(RESPONSE_FILE, 'r', encoding='utf-8') as f:
            responses = json.load(f)
            print(f"\nTotal saved responses: {len(responses)}")
            for i, response in enumerate(responses[-5:], 1):  # Показываем последние 5
                print(f"{i}. Time: {response['timestamp']}, Status: {response.get('status_code', 'Error')}")
    except FileNotFoundError:
        print("No responses file found.")


# Выполняем запрос
if __name__ == "__main__":
    print(f"All responses will be saved to: {RESPONSE_FILE}")

    try:
        request_count = 0
        while True:
            request_count += 1
            print(f"\n=== Request #{request_count} ===")
            make_wayfair_request()

            # Показываем статистику каждые 10 запросов
            if request_count % 10 == 0:
                view_saved_responses()

    except KeyboardInterrupt:
        print(f"\n\nStopped after {request_count} requests")
        print(f"All responses saved to: {RESPONSE_FILE}")
        view_saved_responses()