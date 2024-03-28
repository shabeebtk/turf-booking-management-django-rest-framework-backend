from django.urls import path
from .views import GetUser, Register, verify_email, Login, UserLogout, SendOtp, ChangePassword, SaveFCMToken, getBookings, CancelBooking, startRazorpayment, handle_payment_success, getUserNotification, UpdateUserProfile, OtpChangeEmail, ChangeEmail, SentOtpChangePassword, UserChangePassword, UserChangeProfile, check_username, SendEmailOtp

urlpatterns = [
    path('get_user', GetUser.as_view()),
    path('register', Register.as_view()),
    path('verify_email', verify_email.as_view()),
    path('login', Login.as_view()),
    path('user_logout', UserLogout.as_view()),
    path('sent_otp', SendOtp.as_view()),
    path('change_password', ChangePassword.as_view()),
    path('save_fcmtoken', SaveFCMToken.as_view()),
    path('bookings', getBookings.as_view()),
    path('booking/cancel', CancelBooking.as_view()),
    path('startpayment', startRazorpayment.as_view()),
    path('payment/success', handle_payment_success.as_view()),
    path('notifications', getUserNotification.as_view()),
    path('seen_notification', getUserNotification.as_view()),
    path('update', UpdateUserProfile.as_view()),
    path('change_email', OtpChangeEmail.as_view()),
    path('confirm_change_email', ChangeEmail.as_view()),
    path('change_password_otp', SentOtpChangePassword.as_view()),
    path('confirm_change_password', UserChangePassword.as_view()),
    path('change_user_profile', UserChangeProfile.as_view()),
    path('check_username', check_username.as_view()),
    path('send_email_otp', SendEmailOtp.as_view()),
    
]

