from django.urls import path
from stories.views import(
    HomeView, SingleProductView,ReviewsView,
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('singleproductview/<int:id>/', SingleProductView.as_view(), name='singleproductview'),
    path('reviewsview/', ReviewsView.as_view(), name='reviewsview'),
]
