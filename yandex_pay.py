from yoomoney import Client, Quickpay
from datetime import datetime, date, time
from dotenv import load
import os


load()

token = os.getenv('YOOMONEY_TOKEN')   

client = Client(token)
user = client.account_info()


def payment_yandex(summa: int, label_user: int):
    quickpay = Quickpay(
            receiver="4100116344576756",
            quickpay_form="shop",
            targets="Sponsor this project",
            paymentType="SB",
            sum=summa,
            label=label_user,
            )
    return quickpay.redirected_url


def sucsess_pay(label_user):
    history = client.operation_history(label=label_user)
    for operation in history.operations:
        print(operation.label)
        if operation.status == 'success':
            return True
    return False