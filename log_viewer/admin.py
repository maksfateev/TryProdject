from django.contrib import admin
from django.http import HttpResponseRedirect
from .models import LogViewer


@admin.register(LogViewer)
class LogsViewerAdmin(admin.ModelAdmin):
	def has_add_permission(self, request):
		return False

	def has_change_permission(self, request):
		return False

	def has_module_permission(self, request):
		return request.user.has_module_perms('log_viewer')

	def changelist_view(self, request):
		return HttpResponseRedirect('/logs/')