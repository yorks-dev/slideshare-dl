import os
import re
import sys
import time
import requests


from bs4 import BeautifulSoup

print()

# Get the URLZ
if len(sys.argv) < 2:
    url = input("URL: ")
else:
    url = sys.argv[1]

page = requests.get(url)

soup = BeautifulSoup(page.content, "html.parser")

# getting the Heading of Slide
heading_title = (soup.find("h1", class_=re.compile(r"Title_root"))).text

# extract the list of resolutions source content (un-parsed), soup.findAll returns iterable
# SlideImage_picture__a3aKk is class unlike key for picture tag containing source srcset
list_of_picture_tags_with_unique_class_key = soup.find_all(
    "picture", class_=re.compile(r"SlideImage_picture__a3aKk")
)
highest_resolution_url_array = []  # highest resolutions for each slide

for picture_tag in list_of_picture_tags_with_unique_class_key:
    source_tag = picture_tag.find("source", srcset=True)
    raw_image_url_srcset = source_tag["srcset"]

    resolutions_array = raw_image_url_srcset.split(", ")
    number_of_resolutions = len(resolutions_array)  # 3 for now

    # need to split the highest resolution url into the url and the resolution
    highest_resolution_url = resolutions_array[number_of_resolutions - 1].split(" ")[0]
    highest_resolution_url_array.append(highest_resolution_url)

print("Title : " + str(heading_title))
print(
    "Total number of Slides : " + str(len(list_of_picture_tags_with_unique_class_key))
)

if input("\nProceed to Download ? [Y/N] : ") == "N".lower():
    print("\nDownload Terminated !!")
    sys.exit()

print()

start = time.time()

file_location = "./" + str(heading_title).replace(" ", "-") + "/"
os.mkdir(file_location)
file_address_list = []

for index, url in enumerate(highest_resolution_url_array):
    filename = file_location + (str(heading_title) + "-" + str(index) + ".jpg").replace(
        " ", "-"
    )

    h = requests.head(url, allow_redirects=True)
    header = h.headers
    content_type = header.get("content-type")
    if "image" in content_type.lower():
        with requests.get(url, stream=True) as r:
            with open(filename, "wb") as file:
                # Get the total size, in bytes, from the response header
                total_size = int(r.headers.get("Content-Length"))
                # Define the size of the chunk to iterate over (Mb)
                chunk_size = 100
                # iterate over every chunk and calculate % of total
                for i, chunk in enumerate(r.iter_content(chunk_size=chunk_size)):
                    file.write(chunk)
                    # calculate current percentage
                    c = i * chunk_size / total_size * 100

                    # write current % to console, then flush console
                    sys.stdout.write(f"\rSlide {index + 1} : {round(c, 0)}%")
                    sys.stdout.flush()
        file_address_list.append(filename)
        print()
    else:
        print("Slide " + str(index) + " : FAILED DOWNLOAD")

# Converting to pdf

end = time.time()

print("\n Total time taken : " + str(round((end - start), 2)) + " seconds")
