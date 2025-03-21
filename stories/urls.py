from django.urls import path
from stories.views import(
    HomeView, SingleProductView,ReviewsView, GetColorsBySize, GetPriceBySize, GetPriceByColor
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('singleproductview/<int:id>/', SingleProductView.as_view(), name='singleproductview'),
    path('getcolorsbysize/', GetColorsBySize.as_view(), name='getcolorsbysize'),
    path('getpricebysize/', GetPriceBySize.as_view(), name='getpricebysize'),
    path('getpricebycolor/', GetPriceByColor.as_view(), name='getpricebycolor'),
    path('reviewsview/', ReviewsView.as_view(), name='reviewsview'),
]
