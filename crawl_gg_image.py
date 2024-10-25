import os
import time
import requests  # Import the requests module
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from PIL import Image
import io
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv

def get_images_from_google(driver, delay, max_images):
    def scroll_down(driver):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(delay)

    image_urls = set()
    skips = 0

    while len(image_urls) < max_images:

        thumbnails = driver.find_elements(By.CSS_SELECTOR, '.YQ4gaf')
        for img in thumbnails:
            try:
                width = int(img.get_attribute('width') or 0)
                height = int(img.get_attribute('height') or 0)
                if width >= 150 and height >= 150:
                    img.click()
                    time.sleep(delay)
            except Exception as e:
                print(f"Error clicking thumbnail.")
                continue
            
            images = driver.find_elements(By.CSS_SELECTOR, '.sFlh5c.FyHeAf.iPVvYb')
            for image in images:

                # w = int(image.get_attribute('width') or 0)
                # h = int(image.get_attribute('height') or 0)
                # # if width <= 720 and height <= 720:
                # #     break

                if image.get_attribute('src') in image_urls:
                    break

                if image.get_attribute('src') and 'http' in image.get_attribute('src'):
                    image_urls.add(image.get_attribute('src'))
                    print(f"Found {len(image_urls)} images")
                    print("Name: ", image.get_attribute('alt'))
                    if len(image_urls) > max_images:
                        return image_urls

        scroll_down(driver)
    return image_urls

def download_image(download_path, url, file_name):
    try:
        image_content = requests.get(url).content
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file)

        # Check if the image can be identified and is in a compatible format
        if image.format not in ["JPEG", "PNG"]:
            print(f"Skipping image with unsupported format: {url}")
            return

        file_path = os.path.join(download_path, file_name)  # Use os.path.join to ensure correct path

        with open(file_path, "wb") as f:
            image.save(f, "JPEG")

        print("Success")
        return file_name
    except Exception as e:
        print('FAILED -', e)
        return None


# Ask the user for the search query
search_query = input("Enter your Google Images search query: ")

# Create the 'imgs/' directory if it doesn't exist
download_path = "images"
os.makedirs(download_path, exist_ok=True)

# Create a Chrome driver
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

# Open the Google Images search page with the provided search query
search_url = f"https://www.google.com/search?q={search_query}&tbm=isch"
driver.get(search_url)

# Perform image scraping and downloading
urls = get_images_from_google(driver, 0.5, 5)

image_data = []

for i, url in enumerate(urls):
    file_name = "[" +search_query + "] " + str(i) + ".jpg"
    downloaded_file_name = download_image(download_path, url, file_name)
    if downloaded_file_name:  # Only add to CSV if the image was downloaded subaccessfully
        image_data.append((downloaded_file_name, url))

    

# CREATE .CSV FILE FERE
# csv_file_path = os.path.join(download_path, 'image_data.csv')
# with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
#     writer = csv.writer(csv_file)
#     # writer.writerow(['Image Name', 'Image URL', 'Search Query'])  # Write header
#     for name, url in image_data:
#         writer.writerow([name, url, search_query])  # Write image data


csv_file_path = os.path.join(download_path, 'image_data.csv')

# Check if the file exists and its size
file_is_empty = not os.path.exists(csv_file_path) or os.path.getsize(csv_file_path) == 0

# Open the file in append mode
with open(csv_file_path, mode='a', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    
    # Write header only if the file is empty
    if file_is_empty:
        writer.writerow(['Image Name', 'Image URL', 'Search Query'])  # Write header

    # Write image data
    for name, url in image_data:
        writer.writerow([name, url, search_query])  # Write image data


# Close the driver instance
print("Done")

driver.quit()