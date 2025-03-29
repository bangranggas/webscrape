import html
from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
from django.http import JsonResponse

def show_webdrive(request):    
    return render(request, "drivepage.html")

def show_webof(request):    
    return render(request, "ofpage.html")

def scrape_drive_data():
    # Mengirimkan permintaan HTTP ke halaman lokal
    url = "https://docs.google.com/document/d/1OWaQG-gZwuypDHS0ssmfSSkdm_iLIqEYO1YmauWx54k/mobilebasic"
    response = requests.get(url)
    
    # Pastikan encoding sesuai
    response.encoding = response.apparent_encoding or 'utf-8'
    
    # Parse HTML dengan BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Ambil semua elemen <h3>, <img>, dan <a> untuk setiap album
    albums = {}
    album_count = 1

    h3_elements = soup.find_all("h3")
    img_elements = soup.find_all("img")
    a_elements = soup.find_all("a")  # Mengambil elemen <a> untuk link ke drive album

    # Mengiterasi setiap album
    for i in range(len(h3_elements)):
        # Mengambil data dari elemen-elemen
        album_title = h3_elements[i].get_text(strip=True)
        preview_images = [img_elements[i*2]['src'], img_elements[i*2+1]['src']]  # 2 gambar untuk setiap album
        drive_link = a_elements[i]['href'] if a_elements[i].get('href') else "No Link"

        # Menyusun album dalam format yang sesuai
        albums[album_count] = {
            "title": album_title,
            "preview": preview_images,
            "link": drive_link
        }

        album_count += 1

    return albums

def scrape_drive_data_json(request):
    # Panggil fungsi scrape_local_data untuk mendapatkan data
    scraped_data = scrape_drive_data()

    # Kembalikan data dalam format JSON menggunakan JsonResponse
    return JsonResponse(scraped_data)

def scrape_of_data():
    # Mengirimkan permintaan HTTP ke halaman lokal
    url = "https://docs.google.com/document/d/1v_0v4Xe9twegffXujhDz1Mx5Lha9dlOtdIIZ-eGK-mU/mobilebasic"
    response = requests.get(url)
    
    # Pastikan encoding sesuai
    response.encoding = response.apparent_encoding or 'utf-8'
    
    # Parse HTML dengan BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Ambil semua elemen <h2>, <h3>, <img>, dan <a> untuk setiap album
    categories = {}
    current_category = None
    album_count = 1

    h2_elements = soup.find_all("h2")  # Mengambil kategori
    h3_elements = soup.find_all("h3")  # Mengambil judul album
    img_elements = soup.find_all("img")  # Mengambil gambar preview
    a_elements = soup.find_all("a")  # Mengambil link menuju album drive

    album_index = 0  # Mengindeks album untuk kategori yang sedang diproses

    # Mengiterasi elemen <h2> (kategori) dan mencari album di bawah kategori tersebut
    for i in range(len(h2_elements)):
        category_name = h2_elements[i].get_text(strip=True)
        categories[category_name] = {}

        # Mengambil album untuk kategori ini
        album_start = album_index
        while album_index < len(h3_elements) and (h3_elements[album_index].find_previous("h2") == h2_elements[i]):
            # Mengambil data dari elemen-elemen
            album_title = h3_elements[album_index].get_text(strip=True)

            # Cek apakah ada cukup gambar untuk album ini (2 gambar per album)
            preview_images = []
            # Pastikan ada cukup gambar (2 gambar per album)
            if album_index * 2 < len(img_elements):
                preview_images.append(img_elements[album_index * 2].get('src', 'No Image'))  # Gambar 1
            if album_index * 2 + 1 < len(img_elements):
                preview_images.append(img_elements[album_index * 2 + 1].get('src', 'No Image'))  # Gambar 2

            # Mengambil semua link <a> untuk album ini
            album_links = []
            # Periksa semua <a> setelah <h3> yang relevan dan tambahkan ke dalam list link
            for link in a_elements:
                if link.find_previous("h3") == h3_elements[album_index]:
                    album_links.append(link.get('href', 'No Link'))

            # Menyusun album dalam format yang sesuai
            categories[category_name][album_count] = {
                "title": album_title,
                "preview": preview_images,
                "link": album_links  # Menyimpan link dalam list
            }

            album_index += 1
            album_count += 1

    return categories

def scrape_of_data_json(request):
    # Panggil fungsi scrape_local_data untuk mendapatkan data
    scraped_data = scrape_of_data()

    # Kembalikan data dalam format JSON menggunakan JsonResponse
    return JsonResponse(scraped_data)