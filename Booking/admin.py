from django.contrib import admin
from .models import Restaurant, MenuItem, Table, Guest, Manager, Friendship, Reservation, ReservedTables, Visit,Gadget, Transaction, Game, Events,Opportunities, Apply


admin.site.register(Restaurant)
admin.site.register(MenuItem)
admin.site.register(Gadget)
admin.site.register(Game)
admin.site.register(Transaction)


# changing order of fields for tables
class TableAdmin(admin.ModelAdmin):
    fields = ['restaurant', 'number', 'row', 'column', 'currently_free']

admin.site.register(Table, TableAdmin)

class EventsAdmin(admin.ModelAdmin):
    fields = ['Name', 'date','img']

admin.site.register(Events,EventsAdmin)

admin.site.register(Guest)
admin.site.register(Manager)
admin.site.register(Friendship)
admin.site.register(Apply)

class OpportunityAdmin(admin.ModelAdmin):
    fields = ['name', 'description','location','employer','is_remote','category']


admin.site.register(Opportunities, OpportunityAdmin)

# changing order of fields for reservation
class ReservationAdmin(admin.ModelAdmin):
    fields = ['guest', 'restaurant', 'coming', 'duration']

admin.site.register(Reservation, ReservationAdmin)

admin.site.register(ReservedTables)


# changing order of fields for visit
class VisitAdmin(admin.ModelAdmin):
    fields = ['guest', 'reservation', 'ending_time', 'confirmed', 'grade']

admin.site.register(Visit, VisitAdmin)

