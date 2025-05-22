from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from rest_framework.permissions import AllowAny
from .models import TeacherUsersStats, TeacherTopic
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from django.utils.timezone import is_aware
from django.http import HttpResponse
import io
from rest_framework.generics import RetrieveUpdateAPIView

__all__ = [
    'TeacherUsersStatsView',
    'ExportToExcelView',
    'TeacherEditView',
    'TopicsView',
    'TopicedTeachersView'
]


class TopicsView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = TeacherTopic.objects.all()
    serializer_class = TopicsSerializer

class TeacherUsersStatsView(APIView):
    serializer_class = TeacherUsersStatsSerializer
    permission_classes = [AllowAny]
    def get(self, request):
        stats = TeacherUsersStats.objects.all()
        serializer = self.serializer_class(stats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TeacherEditView(RetrieveUpdateAPIView):
    serializer_class = TeacherEditSerializer
    permission_classes = [AllowAny]  
    queryset = TeacherUsersStats.objects.all()
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        if self.kwargs.get('id') is None:
            return Response(
                {"detail": "ID kiritilishi shart."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().get(request, *args, **kwargs)

class ExportToExcelView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        queryset = TeacherUsersStats.objects.all()

        wb = Workbook()
        ws = wb.active
        ws.title = "TeacherStats"

        headers = [
            'F.I.O', 'Juda yaxshi', 'Yaxshi',
            "O'rtacha", 'Past', 'Yomon',    
        ]
        ws.append(headers)

        header_font = Font(bold=True)
        center_alignment = Alignment(horizontal='center', vertical='center')
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.font = header_font
            cell.alignment = center_alignment
            cell.border = thin_border

        for obj in queryset:
            updated_at = obj.updated_at
            if is_aware(updated_at):
                updated_at = updated_at.replace(tzinfo=None)

            row = [
                obj.full_name,
                obj.juda_ham_qoniqaman,
                obj.ortacha_qoniqaman,
                obj.asosan_qoniqaman,
                obj.qoniqmayman,
                obj.umuman_qoniqaman,
            ]
            ws.append(row)

        for column_cells in ws.columns:
            max_length = 0
            column = column_cells[0].column_letter
            for cell in column_cells:
                try:
                    cell_value = str(cell.value)
                    if cell_value:
                        max_length = max(max_length, len(cell_value))
                    cell.border = thin_border  
                    cell.alignment = Alignment(vertical='center')
                except:
                    pass
            ws.column_dimensions[column].width = max_length + 2

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=teacher_users_stats.xlsx'
        return response
        
class TopicedTeachersView(ListAPIView):
    queryset = TeacherUsersStats.objects.prefetch_related('topics').all()
    permission_classes = [AllowAny]
    serializer_class = TopicedTeachersSerializer
