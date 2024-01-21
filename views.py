from django.conf import settings
import requests
import json


#? sandbox merchant 
if settings.SANDBOX:
    sandbox = 'sandbox'
else:
    sandbox = 'www'


ZP_API_REQUEST = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
ZP_API_VERIFY = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
ZP_API_STARTPAY = f"https://{sandbox}.zarinpal.com/pg/StartPay/"

amount = 1000  # Rial / Required
description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"  # Required
phone = 'YOUR_PHONE_NUMBER'  # Optional
# Important: need to edit for realy server.
CallbackURL = 'http://127.0.0.1:8000/zarinpal/verify/'


def send_request(request):
    data = {
        "MerchantID": settings.MERCHANT,
        "Amount": amount,
        "Description": description,
        "Phone": phone,
        "CallbackURL": CallbackURL,
    }
    data = json.dumps(data)
    # set content length by data
    print('hi')
    headers = {'content-type': 'application/json', 'content-length': str(len(data))}
    try:
        response = requests.post(ZP_API_REQUEST, data=data, headers=headers, timeout=10)
        #print('hii')
        if response.status_code == 200:
            response = response.json()
            #print(response)
            if response['Status'] == 100:
                print("Im here")
                return JsonResponse(data={'status': True, 'url': ZP_API_STARTPAY + str(response['Authority']),
                        'authority': response['Authority']}, status=200,safe=False)
            else:
                return JsonResponse(data={'status': False, 'code': str(response['Status'])},status=response['Status'], safe=False)
        return Response(data=response, status=status.HTTP_200_OK)
    except requests.exceptions.Timeout:
        return JsonResponse(data={'status': False, 'code': 'timeout'}, status=408, safe=False)
    except requests.exceptions.ConnectionError:
        return JsonResponse(data={'status': False, 'code': 'connection error'}, status=502, safe=False)


def verify(request):
    authority = request.GET.get('Authority', '')
    status = request.GET.get('Status', '')

    data = {
        "MerchantID": settings.MERCHANT,
        "Amount": amount,
        "Authority": authority,
    }
    data = json.dumps(data)
    # set content length by data
    headers = {'content-type': 'application/json', 'content-length': str(len(data)) }
    response = requests.post(ZP_API_VERIFY, data=data,headers=headers)

    if response.status_code == 200:
        response = response.json()
        if response['Status'] == 100:
            return JsonResponse(data={'status': True, 'RefID': response['RefID']}, status=200, safe=False)
        else:
            return JsonResponse(data={'status': False, 'code': str(response['Status'])}, status=response['Status'], safe=False)
    return response