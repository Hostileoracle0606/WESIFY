"""
Advanced Image Scraper for Training Data Collection
Uses multiple APIs and services: SerpApi, Bing Image Search, Apify, Pinterest API
"""

import os
import requests
import time
from pathlib import Path
from urllib.parse import urlparse, quote
import json

# Configuration
TRAIN_DIR = "training_data"
CLASSES = ["WES_ANDERSON", "NOT_WES_ANDERSON", "OTHER"]
IMAGES_PER_CLASS = 200  # Target number of images per class
DELAY_BETWEEN_REQUESTS = 0.5  # Seconds to wait between downloads

# Create training directories
for class_name in CLASSES:
    os.makedirs(os.path.join(TRAIN_DIR, class_name), exist_ok=True)


def download_image(url, filepath):
    """Download an image from URL and save to filepath"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/'
        }
        response = requests.get(url, headers=headers, timeout=15, stream=True, allow_redirects=True)
        response.raise_for_status()
        
        # Check if it's actually an image
        content_type = response.headers.get('content-type', '').lower()
        if 'image' not in content_type:
            return False
        
        # Save image
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Verify file was created and has reasonable size
        file_size = os.path.getsize(filepath)
        if 5000 < file_size < 50_000_000:  # Between 5KB and 50MB
            return True
        else:
            if os.path.exists(filepath):
                os.remove(filepath)
            return False
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return False


def scrape_serpapi(keyword, class_name, count=50, api_key=None):
    """
    Scrape images using SerpApi (Google Image Search API)
    Get free API key: https://serpapi.com/
    Free tier: 100 searches/month
    """
    if not api_key:
        return 0
    
    print(f"  Using SerpApi (Google Images) for '{keyword}'...")
    
    class_dir = os.path.join(TRAIN_DIR, class_name)
    existing_count = len([f for f in os.listdir(class_dir) 
                         if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    
    downloaded = 0
    start = 0
    
    while downloaded < count and start < 100:  # Google returns ~20 per page
        try:
            url = "https://serpapi.com/search.json"
            params = {
                'engine': 'google_images',
                'q': keyword,
                'api_key': api_key,
                'num': 20,
                'start': start,
                'safe': 'active',
                'ijn': start // 20  # Image page number
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            images = data.get('images_results', [])
            if not images:
                break
            
            for img in images:
                if downloaded >= count:
                    break
                
                image_url = img.get('original') or img.get('link')
                if not image_url:
                    continue
                
                filename = f"{class_name}_{existing_count + downloaded + 1}.jpg"
                filepath = os.path.join(class_dir, filename)
                
                if download_image(image_url, filepath):
                    downloaded += 1
                    print(f"    [OK] {downloaded}/{count}: {filename}")
                    time.sleep(DELAY_BETWEEN_REQUESTS)
                else:
                    time.sleep(0.2)
            
            start += 20
            time.sleep(1)  # Rate limiting
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                print(f"    [ERROR] SerpApi authentication error. Check your API key.")
            elif response.status_code == 429:
                print(f"    [WARNING] Rate limit reached. Waiting 60 seconds...")
                time.sleep(60)
            else:
                print(f"    [ERROR] {e}")
            break
        except Exception as e:
            print(f"    [ERROR] {str(e)}")
            break
    
    if downloaded > 0:
        print(f"    [OK] SerpApi: {downloaded} images downloaded")
    return downloaded


def scrape_bing_images(keyword, class_name, count=50, api_key=None):
    """
    Scrape images using Bing Image Search API
    Get free API key: https://www.microsoft.com/en-us/bing/apis/bing-image-search-api
    Free tier: 3,000 queries/month
    """
    if not api_key:
        return 0
    
    print(f"  Using Bing Image Search API for '{keyword}'...")
    
    class_dir = os.path.join(TRAIN_DIR, class_name)
    existing_count = len([f for f in os.listdir(class_dir) 
                         if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    
    downloaded = 0
    offset = 0
    
    while downloaded < count and offset < 150:
        try:
            url = "https://api.bing.microsoft.com/v7.0/images/search"
            headers = {
                'Ocp-Apim-Subscription-Key': api_key
            }
            params = {
                'q': keyword,
                'count': 50,  # Max per request
                'offset': offset,
                'imageType': 'Photo',
                'license': 'All',
                'safeSearch': 'Moderate',
                'size': 'Medium',
                'aspect': 'All'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            images = data.get('value', [])
            if not images:
                break
            
            for img in images:
                if downloaded >= count:
                    break
                
                image_url = img.get('contentUrl')
                if not image_url:
                    continue
                
                filename = f"{class_name}_{existing_count + downloaded + 1}.jpg"
                filepath = os.path.join(class_dir, filename)
                
                if download_image(image_url, filepath):
                    downloaded += 1
                    print(f"    [OK] {downloaded}/{count}: {filename}")
                    time.sleep(DELAY_BETWEEN_REQUESTS)
                else:
                    time.sleep(0.2)
            
            offset += len(images)
            time.sleep(1)  # Rate limiting
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                print(f"    [ERROR] Bing API authentication error. Check your API key.")
            elif response.status_code == 429:
                print(f"    [WARNING] Rate limit reached. Waiting 60 seconds...")
                time.sleep(60)
            else:
                print(f"    [ERROR] {e}")
            break
        except Exception as e:
            print(f"    [ERROR] {str(e)}")
            break
    
    if downloaded > 0:
        print(f"    [OK] Bing API: {downloaded} images downloaded")
    return downloaded


def scrape_apify_pinterest(keyword, class_name, count=50, api_key=None):
    """
    Scrape images using Apify Pinterest Scraper
    Get API key: https://apify.com/
    Requires Apify account and actor credits
    """
    if not api_key:
        return 0
    
    print(f"  Using Apify Pinterest Scraper for '{keyword}'...")
    
    try:
        # First, start the actor run
        run_url = "https://api.apify.com/v2/acts/epctex~pinterest-scraper/runs"
        headers = {'Authorization': f'Bearer {api_key}'}
        payload = {
            'search': keyword,
            'maxItems': min(count, 100),
            'proxy': {'useApifyProxy': True}
        }
        
        response = requests.post(run_url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        run_data = response.json()
        run_id = run_data.get('data', {}).get('id')
        
        if not run_id:
            return 0
        
        # Wait for run to complete
        status_url = f"https://api.apify.com/v2/actor-runs/{run_id}"
        max_wait = 300  # 5 minutes max
        waited = 0
        
        while waited < max_wait:
            status_resp = requests.get(status_url, headers=headers, timeout=15)
            status_resp.raise_for_status()
            status_data = status_resp.json()
            status = status_data.get('data', {}).get('status')
            
            if status == 'SUCCEEDED':
                break
            elif status in ['FAILED', 'ABORTED', 'TIMED-OUT']:
                print(f"    [ERROR] Apify run {status.lower()}")
                return 0
            
            time.sleep(5)
            waited += 5
        
        # Get results
        results_url = f"https://api.apify.com/v2/actor-runs/{run_id}/dataset/items"
        results_resp = requests.get(results_url, headers=headers, timeout=15)
        results_resp.raise_for_status()
        results = results_resp.json()
        
        class_dir = os.path.join(TRAIN_DIR, class_name)
        existing_count = len([f for f in os.listdir(class_dir) 
                             if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        
        downloaded = 0
        for item in results[:count]:
            image_url = item.get('image') or item.get('image_url')
            if not image_url:
                continue
            
            filename = f"{class_name}_{existing_count + downloaded + 1}.jpg"
            filepath = os.path.join(class_dir, filename)
            
            if download_image(image_url, filepath):
                downloaded += 1
                print(f"    [OK] {downloaded}/{count}: {filename}")
                time.sleep(DELAY_BETWEEN_REQUESTS)
        
        if downloaded > 0:
            print(f"    [OK] Apify Pinterest: {downloaded} images downloaded")
        return downloaded
        
    except Exception as e:
        print(f"    [ERROR] Apify error: {str(e)}")
        return 0


def scrape_pexels(keyword, class_name, count=50, api_key=None):
    """
    Scrape images using Pexels API
    Get free API key: https://www.pexels.com/api/
    Free tier: Unlimited (with rate limits)
    """
    if not api_key:
        return 0
    
    print(f"  Using Pexels API for '{keyword}'...")
    
    headers = {
        'Authorization': api_key
    }
    
    class_dir = os.path.join(TRAIN_DIR, class_name)
    existing_count = len([f for f in os.listdir(class_dir) 
                         if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    
    downloaded = 0
    page = 1
    per_page = min(80, count)  # Pexels allows up to 80 per page
    
    while downloaded < count and page <= 5:  # Limit to 5 pages
        try:
            url = f"https://api.pexels.com/v1/search?query={quote(keyword)}&per_page={per_page}&page={page}"
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            photos = data.get('photos', [])
            
            if not photos:
                break
            
            for photo in photos:
                if downloaded >= count:
                    break
                
                # Try to get large or medium size
                image_url = photo.get('src', {}).get('large') or photo.get('src', {}).get('medium')
                if not image_url:
                    continue
                
                filename = f"{class_name}_{existing_count + downloaded + 1}.jpg"
                filepath = os.path.join(class_dir, filename)
                
                if download_image(image_url, filepath):
                    downloaded += 1
                    print(f"    [OK] {downloaded}/{count}: {filename}")
                    time.sleep(DELAY_BETWEEN_REQUESTS)
            
            page += 1
            time.sleep(1)  # Rate limiting
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                print(f"    [ERROR] Pexels authentication error. Check your API key.")
            elif response.status_code == 429:
                print(f"    [WARNING] Rate limit reached. Waiting 60 seconds...")
                time.sleep(60)
            else:
                print(f"    [ERROR] {e}")
            break
        except Exception as e:
            print(f"    [ERROR] {str(e)}")
            break
    
    if downloaded > 0:
        print(f"    [OK] Pexels: {downloaded} images downloaded")
    return downloaded


def scrape_pinterest_package(keyword, class_name, count=50):
    """
    Scrape images using pinterest-scrapper Python package
    Install: pip install pinterest-scrapper
    """
    try:
        from pinterest_scraper import PinterestScraper
    except ImportError:
        return 0
    
    print(f"  Using pinterest-scrapper package for '{keyword}'...")
    
    class_dir = os.path.join(TRAIN_DIR, class_name)
    existing_count = len([f for f in os.listdir(class_dir) 
                         if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    
    try:
        scraper = PinterestScraper()
        results = scraper.search(keyword, max_images=count)
        
        downloaded = 0
        for img_data in results:
            if downloaded >= count:
                break
            
            image_url = img_data.get('url') or img_data.get('image_url')
            if not image_url:
                continue
            
            filename = f"{class_name}_{existing_count + downloaded + 1}.jpg"
            filepath = os.path.join(class_dir, filename)
            
            if download_image(image_url, filepath):
                downloaded += 1
                print(f"    [OK] {downloaded}/{count}: {filename}")
                time.sleep(DELAY_BETWEEN_REQUESTS)
        
        if downloaded > 0:
            print(f"    [OK] Pinterest Package: {downloaded} images downloaded")
        return downloaded
        
    except Exception as e:
        print(f"    [ERROR] Pinterest package error: {str(e)}")
        return 0


def main():
    print("="*70)
    print("Wes Anderson Classifier - Advanced Image Scraper")
    print("="*70)
    
    # Load API keys from environment or config
    api_keys = {
        'serpapi': os.environ.get('SERPAPI_KEY'),
        'bing': os.environ.get('BING_SEARCH_KEY'),
        'apify': os.environ.get('APIFY_API_TOKEN'),
        'pexels': os.environ.get('PEXELS_API_KEY'),
    }
    
    # Try loading from config file
    if os.path.exists('scrape_config.json'):
        try:
            with open('scrape_config.json', 'r') as f:
                config = json.load(f)
                api_keys.update(config.get('api_keys', {}))
        except:
            pass
    
    # Show available APIs
    print("\nAvailable API Keys:")
    available_apis = []
    if api_keys['serpapi']:
        print("  [OK] SerpApi (Google Images) - FREE: 100 searches/month")
        available_apis.append('serpapi')
    else:
        print("  [NO] SerpApi - Get free key: https://serpapi.com/")
    
    if api_keys['bing']:
        print("  [OK] Bing Image Search API - FREE: 3,000 queries/month")
        available_apis.append('bing')
    else:
        print("  [NO] Bing API - Get free key: https://www.microsoft.com/en-us/bing/apis/bing-image-search-api")
    
    if api_keys['apify']:
        print("  [OK] Apify (Pinterest/Instagram) - Paid (free credits available)")
        available_apis.append('apify')
    else:
        print("  [NO] Apify - Get key: https://apify.com/")
    
    if api_keys['pexels']:
        print("  [OK] Pexels API - FREE")
        available_apis.append('pexels')
    else:
        print("  [NO] Pexels - Get free key: https://www.pexels.com/api/")
    
    # Check for pinterest-scrapper package
    try:
        import pinterest_scrapper
        print("  [OK] pinterest-scrapper package installed")
        available_apis.append('pinterest_package')
    except ImportError:
        print("  [NO] pinterest-scrapper - Install: pip install pinterest-scrapper")
    
    if not available_apis:
        print("\n[WARNING] No API keys found! Please set environment variables:")
        print("  export SERPAPI_KEY='your_key'")
        print("  export BING_SEARCH_KEY='your_key'")
        print("\nOr edit scrape_config.json with your API keys.")
        response = input("\nContinue anyway (will use limited methods)? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Image search keywords for each class
    search_keywords = {
        "WES_ANDERSON": [
            "wes anderson aesthetic",
            "wes anderson style photography",
            "pastel colors symmetrical",
            "centered composition photography",
            "retro pastel aesthetic",
            "clean minimal background",
            "frontal perspective photo"
        ],
        "NOT_WES_ANDERSON": [
            "everyday photography",
            "natural landscape photos",
            "casual snapshot",
            "modern photography",
            "street photography",
            "documentary photography",
            "real world photos"
        ],
        "OTHER": [
            "film noir style",
            "horror aesthetic",
            "abstract art photography",
            "artistic photography",
            "cinematic photography",
            "vintage photography",
            "different art style"
        ]
    }
    
    # Collect images for each class
    for class_name in CLASSES:
        print(f"\n{'='*70}")
        print(f"Collecting images for: {class_name}")
        print(f"{'='*70}")
        
        class_dir = os.path.join(TRAIN_DIR, class_name)
        existing_count = len([f for f in os.listdir(class_dir) 
                             if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        
        needed = max(0, IMAGES_PER_CLASS - existing_count)
        
        if needed == 0:
            print(f"Already have {existing_count} images for {class_name}. Skipping.")
            continue
        
        print(f"Need {needed} more images (have {existing_count})")
        
        total_downloaded = 0
        
        # Try each keyword
        for keyword in search_keywords.get(class_name, [class_name.lower()]):
            if total_downloaded >= needed:
                break
            
            images_needed = min(needed - total_downloaded, 40)
            
            # Try APIs in order of preference
            if 'serpapi' in available_apis and api_keys['serpapi']:
                downloaded = scrape_serpapi(keyword, class_name, count=images_needed, 
                                           api_key=api_keys['serpapi'])
                total_downloaded += downloaded
                if total_downloaded >= needed:
                    break
                time.sleep(2)
            
            if 'bing' in available_apis and api_keys['bing']:
                downloaded = scrape_bing_images(keyword, class_name, count=images_needed,
                                               api_key=api_keys['bing'])
                total_downloaded += downloaded
                if total_downloaded >= needed:
                    break
                time.sleep(2)
            
            if 'apify' in available_apis and api_keys['apify']:
                downloaded = scrape_apify_pinterest(keyword, class_name, count=images_needed,
                                                   api_key=api_keys['apify'])
                total_downloaded += downloaded
                if total_downloaded >= needed:
                    break
                time.sleep(2)
            
            if 'pexels' in available_apis and api_keys['pexels']:
                downloaded = scrape_pexels(keyword, class_name, count=images_needed,
                                         api_key=api_keys['pexels'])
                total_downloaded += downloaded
                if total_downloaded >= needed:
                    break
                time.sleep(2)
            
            if 'pinterest_package' in available_apis:
                downloaded = scrape_pinterest_package(keyword, class_name, count=images_needed)
                total_downloaded += downloaded
                if total_downloaded >= needed:
                    break
                time.sleep(2)
        
        # Final count
        final_count = len([f for f in os.listdir(class_dir) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        print(f"\n[OK] {class_name}: {final_count} images total ({total_downloaded} new)")
    
    # Summary
    print("\n" + "="*70)
    print("DOWNLOAD SUMMARY")
    print("="*70)
    total = 0
    for class_name in CLASSES:
        class_dir = os.path.join(TRAIN_DIR, class_name)
        count = len([f for f in os.listdir(class_dir) 
                    if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        total += count
        print(f"  {class_name}: {count} images")
    print(f"  TOTAL: {total} images")
    
    MIN_IMAGES_PER_CLASS = 30
    if total >= MIN_IMAGES_PER_CLASS * len(CLASSES):
        print("\n[OK] Ready for training! Run: python train_model.py")
    else:
        print(f"\n[WARNING] Recommended: {MIN_IMAGES_PER_CLASS * len(CLASSES)} images minimum")
        print("  Consider getting API keys for more images.")


if __name__ == "__main__":
    main()
