from django.urls import path
from stories.views import(
    HomeView, SingleProductView,ReviewsView, GetColorsBySize, GetPriceByColor, GetPriceBySize
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('singleproductview/<int:id>/', SingleProductView.as_view(), name='singleproductview'),
    path('getcolorsbysize/', GetColorsBySize.as_view(), name='getcolorsbysize'),
    path('getpricebycolor/', GetPriceByColor.as_view(), name='getpricebycolor'),
    path('getpricebysize/', GetPriceBySize.as_view(), name='getpricebysize'),
    path('reviewsview/', ReviewsView.as_view(), name='reviewsview'),
]
