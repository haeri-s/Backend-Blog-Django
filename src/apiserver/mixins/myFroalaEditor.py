from django.http import HttpResponse
from rest_framework.views import APIView
import json
import sys


# Froala Editor 
class UploadImageView(APIView):
    def post(self, request):
        try:
            print(request.FILES)
        except Exception:
            response = {"error": str(sys.exc_info()[1])}
            print(Exception)
        return HttpResponse(json.dumps(response), content_type="application/json")

