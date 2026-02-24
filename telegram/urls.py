from django.urls import path
from . import views


urlpatterns = [
    path('wallet-callback/', views.wallet_callback),
	path('notification/<int:payment_method_id>/', views.notification),
	# path('payok-callback/', views.payok_callback),
    path('alfateam-callback/', views.alfateam_callback),
	path('xpay-callback/', views.xpay_callback),
	path('onlypays-callback/', views.onlypays_callback),
	path('bridgepay-callback/', views.bridgepay_callback),
	path('bridgepay-tj-callback/', views.bridgepay_tj_callback),
    path('secrett-callback/', views.secrett_callback),
    path('pspware-callback/', views.pspware_callback),
    path('merchant001-callback/', views.merchant001_callback),
	path('bitzone-callback/', views.bitzone_callback),
	path('wellbit-callback/', views.wellbit_callback),
	path('extasypay-callback/', views.extasypay_callback),
	path('infinitypay-callback/', views.infinitypay_callback),
	path('vita-callback/', views.vita_callback),
    path('collybus-callback/', views.collybus_callback),
	path('restart/', views.restart),
	path('update/', views.update),
]