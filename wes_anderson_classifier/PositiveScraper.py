from pinscrape import scraper, Pinterest


keyword = "succession" 
output_folder = "C:\\Users\\Waterloo\\Documents\\python projects\\wes_anderson_data\\not_wes_anderson"
proxies = {}
number_of_workers = 35
images_to_download = 100

def using_search_engine():
    details = scraper.scrape(keyword, output_folder, proxies, number_of_workers, images_to_download)
    if details["isDownloaded"]:
        print("\nDownloading completed !!")
        print(f"\nTotal urls found: {len(details['extracted_urls'])}")
        print(f"\nTotal images downloaded (including duplicate images): {len(details['urls_list'])}")
        print(details)
    else:
        print("\nNothing to download !!", details)


def using_pinterest_apis():
    p = Pinterest(proxies=proxies) # you can also pass `user_agent` here.
    images_url = p.search(keyword, images_to_download)
    p.download(url_list=images_url, number_of_workers=number_of_workers, output_folder=output_folder)

using_search_engine()