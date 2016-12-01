from django.conf.urls import patterns, include, url
from django.contrib import admin
from digispaceapp import views
from django.conf.urls.static import static
from DigiSpace import settings

# from django.views.generic import direct_to_template
from django.views.generic import TemplateView

subscriber_urlpattern = patterns('',
     url(r'^$', 'subscriberapp.views.login_open', name='login_open'),
     url(r'^log-out/', 'subscriberapp.views.signing_out', name='signing_out'),
     url(r'^signin/', 'subscriberapp.views.signin', name='signin'),
     url(r'^add-advert/', 'subscriberapp.views.add_advert', name='add_advert'),
     url(r'^delete-advert/', 'subscriberapp.views.delete_advert', name='delete_advert'),
     url(r'^activate-advert/', 'subscriberapp.views.activate_advert', name='activate_advert'),
     url(r'^get-city/', 'subscriberapp.views.get_city', name='get_city '),
     url(r'^get-pincode/', 'subscriberapp.views.get_pincode', name='get_pincode'),
     url(r'^save-subscription-plan/', 'subscriberapp.views.save_subscription_plan', name='save_subscription_plan'),
     url(r'^save-payment-details/', 'subscriberapp.views.save_payment_details', name='save_payment_details'),
     url(r'^update-payment-details/', 'subscriberapp.views.update_payment_details', name='update_payment_details'),
     url(r'^get-state-place/', 'subscriberapp.views.get_state', name='get_state'),
     url(r'^save-advert/', 'subscriberapp.views.save_advert', name='save_advert'),
     url(r'^update-advert/', 'subscriberapp.views.update_advert', name='update_advert'),
     url(r'^edit-advert/', 'subscriberapp.views.edit_advert', name='edit_advert'),
     url(r'^advert-bookings/', 'subscriberapp.views.advert_bookings', name='advert_bookings'),

     # subscriber-shubham
     url(r'^subscriber-profile/', 'subscriberapp.views.subscriber_profile', name='subscriber_profile'),
     url(r'^update-profile/', 'subscriberapp.views.update_profile', name='update_profile'),
     url(r'^get-state/', 'subscriberapp.views.get_states', name='get_states'),
     url(r'^subscriber-dashboard/', 'subscriberapp.views.subscriber_dashboard', name='subscriber_dashboard'),
     url(r'^subscriber-advert/', 'subscriberapp.views.subscriber_advert', name='subscriber_advert'),
     url(r'^subscriber-advert-stat/', 'subscriberapp.views.subscriber_advert_stat', name='subscriber_advert_stat'),
     url(r'^subscriber-booking/', 'subscriberapp.views.subscriber_booking', name='subscriber_booking'),
     url(r'^update-profile/', 'subscriberapp.views.update_profile', name='update_profile'),
     # forgot Password Shubham
     url(r'^forgot-password/', 'subscriberapp.views.forgot_password', name='forgot_password'),

     # Dashboard Admin
     url(r'^get-admin-filter/', 'subscriberapp.views.get_admin_filter', name='get_admin_filter'),
     url(r'^get-booking-graph-data/', 'subscriberapp.views.get_booking_graph_data', name='get_booking_graph_data'),

     url(r'^renew-subscription/', 'subscriberapp.views.renew_subscription', name='renew_subscription'),
     url(r'^edit-subscription/', 'subscriberapp.views.edit_subscription', name='edit_subscription'),
     url(r'^uploaded-images/', 'subscriberapp.views.uploaded_images', name='uploaded_images'),
     url(r'^uploaded-videos/', 'subscriberapp.views.uploaded_videos', name='uploaded_videos'),
     url(r'^check-category/', 'subscriberapp.views.check_category',name='check_category'),

# Ratecard new urls in subscriber admin
     url(r'^check-category-supplier/', 'subscriberapp.views.check_category_supplier',name='check_category_supplier'),
     url(r'^get-telephone-service-slots/', 'subscriberapp.views.get_telephone_service_slots',name='get_telephone_service_slots'),    
     url(r'^get-premium-subscription-amount/', 'subscriberapp.views.get_premium_subscription_amount',name='get_premium_subscription_amount'),       
     url(r'^get-booked-slots/', 'subscriberapp.views.get_booked_slots',name='get_booked_slots'),
     url(r'^get-telephone-subscription-amount/', 'subscriberapp.views.get_telephone_subscription_amount',name='get_telephone_subscription_amount'),     
     url(r'^get-edit-booked-slots/', 'subscriberapp.views.get_edit_booked_slots',name='get_edit_booked_slots'),     
     url(r'^get-edit-telephone-service-slots/', 'subscriberapp.views.get_edit_telephone_service_slots',name='get_edit_telephone_service_slots'),     
     url(r'^delete-product/', 'subscriberapp.views.delete_product',name='delete_product'),     
     url(r'^delete-nearby-attraction/', 'subscriberapp.views.delete_nearbyatt',name='delete_nearbyatt'),
     url(r'^delete-shopping/', 'subscriberapp.views.delete_shopping',name='delete_shopping'),
     url(r'^delete-school/', 'subscriberapp.views.delete_school',name='delete_school'),
     url(r'^delete-hospital/', 'subscriberapp.views.delete_hospital',name='delete_hospital'),     
     url(r'^update-subscription-plan/', 'subscriberapp.views.update_subscription_plan', name='update_subscription_plan'),
     ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)