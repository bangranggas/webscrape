import time
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from django.shortcuts import render
from django.http import JsonResponse

# Menggunakan requests.Session untuk efisiensi
session = requests.Session()

# View untuk menampilkan halaman web
def show_webdrive(request):    
    return render(request, "drivepage.html")

def show_webof(request):    
    return render(request, "ofpage.html")

def show_webofsearch(request):    
    return render(request, "ofsearchpage.html")

# Fungsi untuk scraping data dari halaman Google Docs (Drive)
def scrape_drive_data():
    start_time = time.time()

    url = "https://docs.google.com/document/d/1OWaQG-gZwuypDHS0ssmfSSkdm_iLIqEYO1YmauWx54k/mobilebasic"
    response = session.get(url)
    response.encoding = response.apparent_encoding or 'utf-8'

    fetch_time = time.time()
    print(f"[scrape_drive_data] HTTP GET: {fetch_time - start_time:.2f}s")

    # Menggunakan lxml sebagai parser
    soup = BeautifulSoup(response.text, "lxml")

    parse_time = time.time()
    print(f"[scrape_drive_data] Parse HTML: {parse_time - fetch_time:.2f}s")

    albums = {}
    album_count = 1

    # Mencari semua elemen <h3>, <img>, dan <a> dalam satu pass
    h3_elements = soup.find_all("h3")
    img_elements = soup.find_all("img")
    a_elements = soup.find_all("a")

    # Mapping h3 ke gambar dan link terkait
    h3_to_images = defaultdict(list)
    h3_to_links = defaultdict(list)

    # Mengambil gambar dan link terkait dengan h3
    img_index = 0
    for h3 in h3_elements:
        preview_images = []
        while img_index < len(img_elements) and len(preview_images) < 2:
            preview_images.append(img_elements[img_index].get('src', 'No Image'))
            img_index += 1
        h3_to_images[h3] = preview_images

    # Mengambil link terkait dengan h3
    for a in a_elements:
        parent_h3 = a.find_previous("h3")
        if parent_h3:
            h3_to_links[parent_h3].append(a.get_text(strip=True))

    # Menyusun album dari data yang telah dikumpulkan
    for h3 in h3_elements:
        album_title = h3.get_text(strip=True)
        preview_images = h3_to_images[h3]
        album_links = h3_to_links[h3]

        albums[album_count] = {
            "title": album_title,
            "preview": preview_images,
            "links": album_links
        }
        album_count += 1

    build_time = time.time()
    print(f"[scrape_drive_data] Build result: {build_time - parse_time:.2f}s")
    print(f"[scrape_drive_data] Total time: {build_time - start_time:.2f}s")

    return albums

# Fungsi untuk mengembalikan data scrape dalam format JSON
def scrape_drive_data_json(request):
    # Panggil fungsi scrape_drive_data untuk mendapatkan data
    scraped_data = scrape_drive_data()

    # Kembalikan data dalam format JSON menggunakan JsonResponse
    return JsonResponse(scraped_data)

# Fungsi untuk scraping data dari halaman Google Docs (OF)
def scrape_of_data():
    start_time = time.time()

    url = "https://docs.google.com/document/d/1v_0v4Xe9twegffXujhDz1Mx5Lha9dlOtdIIZ-eGK-mU/mobilebasic"
    response = session.get(url)
    response.encoding = response.apparent_encoding or 'utf-8'

    fetch_time = time.time()
    print(f"[scrape_of_data] HTTP GET: {fetch_time - start_time:.2f}s")

    # Menggunakan lxml sebagai parser
    soup = BeautifulSoup(response.text, "lxml")

    parse_time = time.time()
    print(f"[scrape_of_data] Parse HTML: {parse_time - fetch_time:.2f}s")

    categories = {}
    album_count = 1

    # Mencari semua elemen <h2>, <h3>, <img>, dan <a> dalam satu pass
    h2_elements = soup.find_all("h2")
    h3_list = []
    img_elements = soup.find_all("img")
    a_elements = soup.find_all("a")

    # Mapping h3 ke gambar dan link terkait
    h3_to_images = defaultdict(list)
    h3_to_links = defaultdict(list)

    # Mengambil gambar dan link terkait dengan h3
    img_index = 0
    for h3 in soup.find_all("h3"):
        preview_images = []
        while img_index < len(img_elements) and len(preview_images) < 2:
            preview_images.append(img_elements[img_index].get('src', 'No Image'))
            img_index += 1
        h3_to_images[h3] = preview_images

    # Mengambil link terkait dengan h3
    for a in a_elements:
        parent_h3 = a.find_previous("h3")
        if parent_h3:
            h3_to_links[parent_h3].append(a.get_text(strip=True))

    # Menyusun kategori dan album dari data yang telah dikumpulkan
    category_map = defaultdict(list)
    for h3 in soup.find_all("h3"):
        parent_h2 = h3.find_previous("h2")
        if parent_h2:
            category_map[parent_h2].append(h3)

    # Menyusun kategori dan album
    for h2 in h2_elements:
        category_name = h2.get_text(strip=True)
        categories[category_name] = {}

        for h3 in category_map[h2]:
            album_title = h3.get_text(strip=True)

            preview_images = h3_to_images.get(h3, [])
            album_links = h3_to_links.get(h3, [])

            categories[category_name][album_count] = {
                "title": album_title,
                "preview": preview_images,
                "link": album_links
            }
            album_count += 1

    build_time = time.time()
    print(f"[scrape_of_data] Build result: {build_time - parse_time:.2f}s")
    print(f"[scrape_of_data] Total time: {build_time - start_time:.2f}s")

    return categories

# Fungsi untuk mengembalikan data scrape OF dalam format JSON
def scrape_of_data_json(request):
    # Panggil fungsi scrape_of_data untuk mendapatkan data
    scraped_data = scrape_of_data()

    # Kembalikan data dalam format JSON menggunakan JsonResponse
    return JsonResponse(scraped_data)

# Fungsi untuk scraping data pencarian OF
def scrape_of_search_data():
    start_time = time.time()

    url = "https://docs.google.com/document/d/1HTC847zYHuwPmui2-p0h0-PD5HQ0v27MQpWLlZE9SgI/mobilebasic"
    response = session.get(url)
    response.encoding = response.apparent_encoding or 'utf-8'

    fetch_time = time.time()
    print(f"[scrape_of_search_data] HTTP GET: {fetch_time - start_time:.2f}s")

    # Menggunakan lxml sebagai parser
    soup = BeautifulSoup(response.text, "lxml")

    parse_time = time.time()
    print(f"[scrape_of_search_data] Parse HTML: {parse_time - fetch_time:.2f}s")

    titles = {}
    item_count = 1

    # Mencari semua elemen <h2> dan <p> dalam satu pass
    h2_elements = soup.find_all("h2")
    p_elements = soup.find_all("p")

    # Mapping p untuk IMG dan link ke h2
    h2_to_img_link = {}
    h2_to_page_link = {}

    # Mengambil gambar dan link terkait dengan h2
    for p in p_elements:
        if "IMG :" in p.get_text():
            img_text = p.get_text()
            img_parts = img_text.split("IMG :")
            if len(img_parts) > 1:
                h2 = p.find_previous("h2")
                if h2:
                    h2_to_img_link[h2] = img_parts[1].strip()

        if "IMG :" not in p.get_text():
            a_tag = p.find("span")
            if a_tag:
                page_link = a_tag.get_text(strip=True)
                h2 = p.find_previous("h2")
                if h2:
                    h2_to_page_link[h2] = page_link

    # Menyusun data dari h2
    for h2 in h2_elements:
        title = h2.get_text(strip=True)
        img_link = h2_to_img_link.get(h2, None)
        page_link = h2_to_page_link.get(h2, None)

        titles[item_count] = {
            "title": title,
            "image": img_link,
            "link": page_link
        }
        item_count += 1

    build_time = time.time()
    print(f"[scrape_of_search_data] Build result: {build_time - parse_time:.2f}s")
    print(f"[scrape_of_search_data] Total time: {build_time - start_time:.2f}s")

    return titles

# Fungsi untuk mengembalikan data pencarian OF dalam format JSON
def scrape_of_search_data_json(request):
    # Panggil fungsi scrape_of_search_data untuk mendapatkan data
    scraped_data = scrape_of_search_data()

    # Kembalikan data dalam format JSON menggunakan JsonResponse
    return JsonResponse(scraped_data)
