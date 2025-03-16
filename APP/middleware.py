from django.shortcuts import redirect
from django.conf import settings

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # استثناء صفحات تسجيل الدخول ولوحة التحكم
        allowed_paths = [settings.LOGIN_URL, "/admin/"]

        if not request.user.is_authenticated and request.path not in allowed_paths:
            return redirect(settings.LOGIN_URL)  # إعادة التوجيه إلى صفحة تسجيل الدخول

        return self.get_response(request)
