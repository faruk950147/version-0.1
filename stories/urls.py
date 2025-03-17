from django.urls import path
from stories.views import(
    HomeView, SingleProductView,ReviewsView, get_colors_by_size
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('singleproductview/<int:id>/', SingleProductView.as_view(), name='singleproductview'),
    path('get-colors-by-size/', get_colors_by_size, name='get_colors_by_size'),
    path('reviewsview/', ReviewsView.as_view(), name='reviewsview'),
]
