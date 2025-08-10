from django.urls import path
from scraping.views import show_webdrive, show_webof,show_webofsearch, scrape_drive_data_json, scrape_of_data_json, scrape_of_search_data_json

app_name = 'scraping'

urlpatterns = [
    path('gdrive/', show_webdrive, name='show_webdrive'),
    path('', show_webof, name='show_webof'),
    path('custom', show_webofsearch, name='show_webofsearch'),
    path('scrape-data-drive/', scrape_drive_data_json, name='scrape_data_drive'),
    path('scrape-data-of/', scrape_of_data_json, name='scrape_data_of'),
    path('scrape-data-custom/', scrape_of_search_data_json, name='scrape_search_data'),
]