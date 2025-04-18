import html
from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
from django.http import JsonResponse

def show_webdrive(request):    
    return render(request, "drivepage.html")

def show_webof(request):    
    return render(request, "ofpage.html")

def show_webofsearch(request):    
    return render(request, "ofsearchpage.html")

def scrape_drive_data():
    # Mengirimkan permintaan HTTP ke halaman Google Docs
    url = "https://docs.google.com/document/d/1OWaQG-gZwuypDHS0ssmfSSkdm_iLIqEYO1YmauWx54k/mobilebasic"
    response = requests.get(url)
    
    # Pastikan encoding sesuai
    response.encoding = response.apparent_encoding or 'utf-8'
    
    # Parse HTML dengan BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Ambil semua elemen <h3>, <img> untuk setiap album
    albums = {}
    album_count = 1

    h3_elements = soup.find_all("h3")

    # Mengiterasi setiap judul album (h3)
    for i, h3 in enumerate(h3_elements):
        # Mengambil judul album
        album_title = h3.get_text(strip=True)
        
        # Mencari semua elemen <img> yang terkait dengan judul ini
        # Ambil 2 gambar setelah h3 ini, tetapi sebelum h3 berikutnya atau akhir dokumen
        preview_images = []
        current_element = h3.next_sibling
        
        # Cari 2 gambar
        img_count = 0
        while current_element and img_count < 2:
            if current_element.name == "img":
                preview_images.append(current_element.get('src', 'No Image'))
                img_count += 1
            # Berhenti jika menemukan h3 berikutnya
            elif current_element.name == "h3":
                break
            current_element = current_element.next_sibling
        
        # Jika tidak menemukan cukup gambar, cari lebih spesifik
        if len(preview_images) < 2:
            # Cari 2 gambar terdekat setelah h3 ini
            next_imgs = soup.find_all("img")
            start_idx = 0
            for idx, img in enumerate(next_imgs):
                if img.find_previous("h3") == h3:
                    start_idx = idx
                    break
            
            # Ambil 2 gambar dari posisi ini
            if start_idx + 1 < len(next_imgs):
                preview_images = [
                    next_imgs[start_idx].get('src', 'No Image'),
                    next_imgs[start_idx + 1].get('src', 'No Image')
                ]
        
        # Cari semua link <a> yang terkait dengan judul ini
        # Link dianggap terkait jika h3 terdekat di atasnya adalah judul ini
        album_links = []
        
        # Temukan h3 berikutnya (jika ada)
        next_h3 = h3.find_next("h3")
        
        # Cari semua link setelah h3 ini dan sebelum h3 berikutnya
        current_link = h3.find_next("a")
        while current_link and (next_h3 is None or current_link.sourceline < next_h3.sourceline):
            link_text = current_link.get_text(strip=True)
            if link_text:  # Pastikan link memiliki teks
                album_links.append(link_text)
            current_link = current_link.find_next("a")
        
        # Jika tidak ada link yang ditemukan dengan cara di atas
        # Coba cara alternatif berdasarkan hubungan previous h3
        if not album_links:
            for link in soup.find_all("a"):
                if link.find_previous("h3") == h3:
                    link_text = link.get_text(strip=True)
                    if link_text and link_text not in album_links:
                        album_links.append(link_text)
        
        # Menyusun album dalam format yang sesuai
        albums[album_count] = {
            "title": album_title,
            "preview": preview_images,
            "links": album_links  # Menyimpan semua link
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
                    album_links.append(link.get_text(strip=True))

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

def scrape_of_search_data():
    # Mengirimkan permintaan HTTP ke halaman
    url = "https://docs.google.com/document/d/145DaDkBaGr9B3XxsC8ICvhcUyr1uVwNw3eAOCM37_lE/mobilebasic"  # Ganti dengan URL yang sesuai
    response = requests.get(url)
    
    # Pastikan encoding sesuai
    response.encoding = response.apparent_encoding or 'utf-8'
    
    # Parse HTML dengan BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Ambil semua elemen <h2> untuk judul
    titles = {}
    item_count = 1

    h2_elements = soup.find_all("h2")

    # Mengiterasi setiap judul (h2)
    for h2 in h2_elements:
        # Mengambil judul
        title = h2.get_text(strip=True)
        
        # Mencari elemen <p> setelah h2 yang berisi "IMG :"
        img_link = None
        current_element = h2.next_sibling
        
        while current_element and not img_link:
            if current_element.name == "p" and "IMG :" in current_element.get_text():
                # Ambil link gambar (teks setelah "IMG :")
                img_text = current_element.get_text()
                img_parts = img_text.split("IMG :")
                if len(img_parts) > 1:
                    img_link = img_parts[1].strip()
            
            # Berhenti jika menemukan h2 berikutnya
            elif current_element.name == "h2":
                break
                
            current_element = current_element.next_sibling
        
        # Mencari elemen <a> setelah h2 ini dan sebelum h2 berikutnya
        page_link = None
        current_element = h2.next_sibling
        
        while current_element and not page_link:
            if current_element.name == "p" and "IMG :" not in current_element.get_text():
                a_tag = current_element.find("span")
                if a_tag:
                    # Ambil teks dari tag <a>, bukan href
                    page_link = a_tag.get_text()
                    break
            
            # Berhenti jika menemukan h2 berikutnya
            elif current_element.name == "h2":
                break
                
            current_element = current_element.next_sibling
        
        # Menyusun data dalam format yang sesuai
        titles[item_count] = {
            "title": title,
            "image": img_link,
            "link": page_link
        }
        
        item_count += 1

    return titles

def scrape_of_search_data_json(request):
    # Panggil fungsi scrape_of_search_data untuk mendapatkan data
    scraped_data = scrape_of_search_data()

    # Kembalikan data dalam format JSON menggunakan JsonResponse
    return JsonResponse(scraped_data)