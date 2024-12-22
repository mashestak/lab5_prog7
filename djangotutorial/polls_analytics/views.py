from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from polls.models import Question, Choice

class PollStatisticsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        poll_id = request.query_params.get('poll_id')
        if not poll_id:
            return Response({"error": "Poll ID is required"}, status=400)

        try:
            poll = Question.objects.get(id=poll_id)
            votes = Choice.objects.filter(poll=poll)
            total_votes = votes.count()
            options = poll.options.all()
            results = [
                {
                    "option": option.text,
                    "votes": votes.filter(option=option).count(),
                    "percentage": round(
                        votes.filter(option=option).count() / total_votes * 100, 2
                    ) if total_votes else 0
                }
                for option in options
            ]
            return Response({
                "poll": poll.title,
                "total_votes": total_votes,
                "results": results,
            })
        except Question.DoesNotExist:
            return Response({"error": "Poll not found"}, status=404)

from rest_framework.generics import ListAPIView
from polls.models import Question
from polls.serializers import PollSerializer

class PollFilterSortAPIView(ListAPIView):
    serializer_class = PollSerializer

    def get_queryset(self):
        queryset = Question.objects.all()
        sort_by = self.request.query_params.get('sort_by', 'date_created')
        filter_by_date = self.request.query_params.get('date')

        if filter_by_date:
            queryset = queryset.filter(date_created__date=filter_by_date)
        if sort_by in ['date_created', 'popularity']:
            queryset = queryset.order_by(sort_by)
        return queryset


import matplotlib.pyplot as plt
import io
import base64
from django.http import JsonResponse

class PollGraphAPIView(APIView):
    def get(self, request, *args, **kwargs):
        poll_id = request.query_params.get('poll_id')
        if not poll_id:
            return Response({"error": "Poll ID is required"}, status=400)

        try:
            poll = Question.objects.get(id=poll_id)
            votes = Choice.objects.filter(poll=poll)
            total_votes = votes.count()
            options = poll.options.all()
            labels = [option.text for option in options]
            sizes = [votes.filter(option=option).count() for option in options]

            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, autopct='%1.1f%%')
            ax.axis('equal')  # Equal aspect ratio ensures pie is drawn as a circle.

            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            buf.close()

            return JsonResponse({
                "poll": poll.title,
                "graph": image_base64,
            })
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=404)

import csv
from django.http import HttpResponse
from polls.models import Question, Choice

class PollExportAPIView(APIView):
    def get(self, request, *args, **kwargs):
        export_format = request.query_params.get('format', 'csv')
        poll_id = request.query_params.get('poll_id')
        if not poll_id:
            return Response({"error": "Question ID is required"}, status=400)

        try:
            poll = Question.objects.get(id=poll_id)
            votes = Choice.objects.filter(poll=poll)
            options = poll.options.all()

            if export_format == 'csv':
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="poll_{poll_id}.csv"'
                writer = csv.writer(response)
                writer.writerow(['Option', 'Votes'])
                for option in options:
                    writer.writerow([option.text, votes.filter(option=option).count()])
                return response
            elif export_format == 'json':
                data = {
                    "poll": poll.title,
                    "options": [
                        {"option": option.text, "votes": votes.filter(option=option).count()}
                        for option in options
                    ],
                }
                return Response(data)
            else:
                return Response({"error": "Invalid format"}, status=400)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=404)
