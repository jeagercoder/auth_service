
from rest_framework.routers import SimpleRouter

router = SimpleRouter(trailing_slash=False)

urlpatterns = [] + router.urls
