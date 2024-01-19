from django.template.loader import get_template
from django.http import HttpResponse
from django.views import View
from weasyprint import HTML

class PdfView(View):
    def get(self, request, *args, **kwargs):
        template = get_template('analytics/index_graph.html')
        context = {
            # your context data goes here
        }
        html = template.render(context)
        pdf = HTML(string=html).write_pdf()
        response = HttpResponse(pdf, content_type='application/pdf')
        return response