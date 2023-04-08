import os

import configparser

import os
import string
import secrets

import requests

import spacy

import praw
import requests

config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
config = configparser.ConfigParser()
config.read(config_path)

CLIENT_ID = config["REDDIT"]["CLIENT_ID"]
CLIENT_SECRET = config["REDDIT"]["CLIENT_SECRET"]

nlp = spacy.load("en_core_web_sm")

reddit = praw.Reddit(client_id=CLIENT_ID,
                     client_secret=CLIENT_SECRET,
                     user_agent='MyApp/1.0.0')




def remove_invalid_characters(video_name):
    video_name = video_name.replace('\u200b', '')

    video_name = video_name.replace('\u200d', '')

    video_name = video_name.replace(':', '')
    video_name = video_name.replace('(', '')
    video_name = video_name.replace("'", '')
    video_name = video_name.replace('.', '')

    video_name = video_name.replace('?', '')

    video_name = video_name.replace('/', '')

    video_name = video_name.replace('*', '')

    video_name = video_name.replace('|', '')

    video_name = video_name.replace('>', '')

    video_name = video_name.replace('<', '')

    video_name = video_name.replace('"', '')

    return video_name.strip()



def download_content(posts, download_folder):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    for post in posts:
        title = post['title']

        # Replace any invalid characters in the title
        cleaned_title = remove_invalid_characters(title)

        # Create a folder for each title
        title_folder = os.path.join(download_folder, cleaned_title)
        if not os.path.exists(title_folder):
            os.makedirs(title_folder)

        urls = post['url'] if isinstance(post['url'], list) else [post['url']]

        for i, url in enumerate(urls):
            print(url)
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                file_extension = os.path.splitext(url)[1]
                if "?" in file_extension:
                    file_extension = file_extension.split("?")[0]
                print(file_extension)
                # Generate a random file name
                random_filename = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
                filename = f"{random_filename}{file_extension}"
                print(f"Downloading {filename} to {title_folder}")

                file_path = os.path.join(title_folder, filename)

                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                print(f"Downloaded {filename} to {title_folder}")


def process_post(post):
    url = post.url
    post.title = remove_invalid_characters(post.title)
    if len(post.title) > 250:
        post.title = post.title[:250]
    if '/comments/' in url:
        return None

    if 'imgur.com' in url and '.gifv' not in url:
        url = f'{url}.jpg'
    elif 'v.redd.it' in url:
        url = f'{url}/DASH_720.mp4'
    elif post.is_video:
        url = post.media['reddit_video']['fallback_url']
    elif 'reddit.com/gallery/' in post.url:
        if not hasattr(post, 'media_metadata'):
            return None
        media_urls = []
        for item in post.media_metadata.values():
            media_url = item['s']['u']
            media_urls.append(media_url)

        return {'title': post.title, 'url': media_urls}


    return {'title': post.title, 'url': url}


def filter_posts(posts, filter):
    filtered_posts = []

    for post in posts:
        title = post.title.lower()
        if not filter or any(keyword.lower() in title for keyword in filter):
            processed_post = process_post(post)
            if processed_post is not None:
                filtered_posts.append(processed_post)

    return filtered_posts


def get_top_posts(subreddit, filter):
    week_top_posts = reddit.subreddit(subreddit).top(time_filter='week')
    today_top_posts = reddit.subreddit(subreddit).top(time_filter='day')

    filtered_week_posts = filter_posts(week_top_posts, filter)
    filtered_today_posts = filter_posts(today_top_posts, filter)

    all_post_info = filtered_week_posts + filtered_today_posts
    return all_post_info


def get_all_top_posts(subreddits, filter):
    all_posts = []
    for subreddit in subreddits:
        posts = get_top_posts(subreddit, filter)
        all_posts.extend(posts)
    return all_posts



def main():
    dedicated_subreddits = ['reptiles']
    other_subreddits = ['aww', 'funny', 'gifs', 'dogs', 'cats']
    filter = ['cat', 'dog', 'animal', 'pet']

    posts = get_all_top_posts(dedicated_subreddits, [])
    # print(posts)

    # posts.extend(get_all_top_posts(other_subreddits, filter))

    print(len(posts))
    download_content(posts, "posts")


main()
