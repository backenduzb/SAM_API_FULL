
from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _
from datetime import datetime, timedelta

class CustomUpdatedAtFilter(SimpleListFilter):
    title = _('Updated at') 
    parameter_name = 'updated_at'

    def lookups(self, request, model_admin):
        return [
            ('today', _('Bugun')),
            ('last_7_days', _('Oxirgi 7 kun')),
            ('this_month', _('Ushbu oy')),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        now = datetime.now()

        if value == 'today':
            return queryset.filter(updated_at__date=now.date())
        elif value == 'last_7_days':
            return queryset.filter(updated_at__gte=now - timedelta(days=7))
        elif value == 'this_month':
            return queryset.filter(updated_at__year=now.year, updated_at__month=now.month)
        return queryset
