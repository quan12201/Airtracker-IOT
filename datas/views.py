from util.HiveMQ import PublicClient
import csv
from django.apps import apps

from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.core import serializers
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from background_task import background

from datas.models import Data

from datas.serializers import DataSerializer
from devices.models import Device
from iotdashboard.debug import debug


def ip_address(request):
    """
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip


def datalist(request):
    refresh_data()

    # Query all data
    datas = Data.objects.all()
    return render(request, 'back/data_list.html', locals())


class DataList(APIView):
    def get(self, request, format=None):
        if 'last' in request.GET:
            datas = Data.objects.all()[:1]
        elif 'result' in request.GET:
            datas = Data.objects.all()[:int(request.GET['result'])]
        else:
            datas = Data.objects.all()

        serializer = DataSerializer(datas, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        try:
            api_key = request.data['api_key']
            device = get_object_or_404(Device, api_key=api_key, enable=True)
            request.data['device'] = device.pk
            request.data['remote_address'] = ip_address(request)
            serializer = DataSerializer(data=request.data)
            debug(serializer)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            msg_err = {'err': 'API KEY not found!'}
            return Response(msg_err, status=status.HTTP_400_BAD_REQUEST)


class DataDetail(APIView):
    """
    Retrieve, update or delete a datas instance.
    """

    def get_object(self, pk):
        try:
            return Data.objects.get(pk=pk)
        except Data.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        datas = self.get_object(pk)
        serializer = DataSerializer(datas)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        datas = self.get_object(pk)
        serializer = DataSerializer(datas, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        datas = self.get_object(pk)
        datas.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def data_chart(request, id):
    refresh_data()

    device = Device.objects.get(pk=id)
    datas = Data.objects.filter(device=device)[:10]
    
    print(datas[0].pub_date.date())
    avg_1 = 0
    avg_2 = 0
    avg_3 = 0
    avg_4 = 0
    avg_5 = 0
    avg_6 = 0
    for data in datas:
        avg_1 += float(data.field_1)
        avg_2 += float(data.field_2)
        avg_3 += float(data.field_3)
        avg_4 += float(data.field_4)
        avg_5 += float(data.field_5)
        avg_6 += float(data.field_6)

    avg_1 = round(avg_1 / 10, 2)
    avg_2 = round(avg_2 / 10, 2)
    avg_3 = round(avg_3 / 10, 2)
    avg_4 = round(avg_4 / 10, 2)
    avg_5 = round(avg_5 / 10, 2)
    avg_6 = round(avg_6 / 10, 2)


    return render(request, 'back/data_chart.html', locals())


def data_chart_ajax(request, id):
    device = Device.objects.get(pk=id)
    datas = Data.objects.filter(device=device)[:10]

    labels = []
    data_1 = []
    data_2 = []
    data_3 = []
    data_4 = []
    data_5 = []
    data_6 = []
    # labels.append(datas[9].pub_date)
    # labels.append(datas[0].pub_date)


    for i in range(len(datas) - 1, -1, -1):
        pub_time = datas[i].pub_date.strftime("%m-%d-%Y:%H:%M:%S")
        # labels.append(pub_time)
        labels.append("")
        data_1.append(datas[i].field_1)
        data_2.append(datas[i].field_2)
        data_3.append(datas[i].field_3)
        data_4.append(datas[i].field_4)
        data_5.append(datas[i].field_5)
        data_6.append(datas[i].field_6)
    
    print(len(labels))

    labels[0] = datas[9].pub_date.strftime("%d-%m-%Y:%H:%M:%S")
    labels[9] = datas[0].pub_date.strftime("%d-%m-%Y:%H:%M:%S")


    return JsonResponse(data={
        'labels': labels,
        'data_1': data_1,
        'data_2': data_2,
        'data_3': data_3,
        'data_4': data_4,
        'data_5': data_5,
        'data_6': data_6
    })

def export(request, model):
    """
    :param request:
    :return:
    """
    model = apps.get_model(app_label=model + 's', model_name=model)
    if request.GET['format'] == 'csv':
        return csv_response()
    else:
        data = serializers.serialize(request.GET['format'], model.objects.all()[:100])

    return JsonResponse({'response_data': data})

@background(schedule=1000)
def refresh_data():
    print("Refreshing data")
    # Renew data
    # data_list = Client().get_messages()
    # for data in data_list:
    #     DataSerializer.create_new_data(data)
    client = PublicClient()
    client.loop()


def csv_response():
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="data.csv"'},
    )
    return Data.get_as_csv(response)
