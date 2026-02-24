from django.db import models


class LogViewer(models.Model):
	class Meta:
		managed = False
		default_permissions = ()
		permissions = [['view', 'Access admin page']]
		verbose_name = 'Журналы'
		verbose_name_plural = 'Журналы'