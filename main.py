import os
import requests
import csv
import time
import sys
from colorama import init, Fore, Style
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

# Initialize colorama
init(autoreset=True)

# Load environment variables
load_dotenv(dotenv_path=".env.local")
USERNAME = os.getenv("GITHUB_USERNAME")
TOKEN = os.getenv("GITHUB_TOKEN")

# Validate credentials
if not USERNAME or not TOKEN:
    print(Fore.RED + "❌ Error: GITHUB_USERNAME or GITHUB_TOKEN not set correctly in .env.local")
    exit(1)

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"token {TOKEN}"
}

def print_banner():
    banner = """
  ██████╗ ██╗████████╗██╗  ██╗██╗   ██╗██████╗                                          
 ██╔════╝ ██║╚══██╔══╝██║  ██║██║   ██║██╔══██╗                                         
 ██║  ███╗██║   ██║   ███████║██║   ██║██████╔╝                                         
 ██║   ██║██║   ██║   ██╔══██║██║   ██║██╔══██╗                                         
 ╚██████╔╝██║   ██║   ██║  ██║╚██████╔╝██████╔╝                                         
  ╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═════╝                                          
                                                                                        
 ██╗   ██╗███╗   ██╗███████╗ ██████╗ ██╗     ██╗      ██████╗ ██╗    ██╗███████╗██████╗ 
 ██║   ██║████╗  ██║██╔════╝██╔═══██╗██║     ██║     ██╔═══██╗██║    ██║██╔════╝██╔══██╗
 ██║   ██║██╔██╗ ██║█████╗  ██║   ██║██║     ██║     ██║   ██║██║ █╗ ██║█████╗  ██║  ██║
 ██║   ██║██║╚██╗██║██╔══╝  ██║   ██║██║     ██║     ██║   ██║██║███╗██║██╔══╝  ██║  ██║
 ╚██████╔╝██║ ╚████║██║     ╚██████╔╝███████╗███████╗╚██████╔╝╚███╔███╔╝███████╗██████╔╝
  ╚═════╝ ╚═╝  ╚═══╝╚═╝      ╚═════╝ ╚══════╝╚══════╝ ╚═════╝  ╚══╝╚══╝ ╚══════╝╚═════╝                                                                                                                                       
"""
    print(Fore.CYAN + banner)
    print(Fore.MAGENTA + "  → Created by @marichu_kt · GitHub: https://github.com/marichu-kt/GitHub-Unfollowed\n")

def simulate_loading(message, duration=2):
    spinner = ["|", "/", "-", "\\"]
    t_end = time.time() + duration
    idx = 0
    while time.time() < t_end:
        sys.stdout.write(f"\r{message} {spinner[idx % len(spinner)]}")
        sys.stdout.flush()
        time.sleep(0.2)
        idx += 1
    sys.stdout.write(f"\r{message} ✓\n")
    sys.stdout.flush()

def get_paginated_list(url_base):
    users = []
    page = 1
    while True:
        url = f"{url_base}?per_page=100&page={page}"
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print(Fore.RED + f"❌ Error ({res.status_code}) while accessing: {url}")
            break
        page_data = res.json()
        if not page_data:
            break
        users.extend([user["login"] for user in page_data])
        page += 1
    return users

def get_following():
    simulate_loading("📥 Fetching users you FOLLOW...")
    return get_paginated_list(f"https://api.github.com/users/{USERNAME}/following")

def get_followers():
    simulate_loading("📥 Fetching users who FOLLOW you...")
    return get_paginated_list(f"https://api.github.com/users/{USERNAME}/followers")

def get_user_details(username):
    url = f"https://api.github.com/users/{username}"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        return {
            "login": data.get("login"),
            "name": data.get("name"),
            "followers": data.get("followers"),
            "following": data.get("following"),
            "html_url": data.get("html_url")
        }
    else:
        return {
            "login": username,
            "name": "",
            "followers": "",
            "following": "",
            "html_url": ""
        }

def fetch_all_user_details(usernames, max_workers=10):
    detailed_users = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(get_user_details, user): user for user in usernames}
        for future in as_completed(futures):
            try:
                user_info = future.result()
                detailed_users.append(user_info)
            except Exception as e:
                print(Fore.RED + f"⚠️  Error retrieving user data: {e}")
    return detailed_users

def export_to_txt(users, filename):
    with open(filename, "w", encoding="utf-8") as f:
        for user in users:
            f.write(f"{user['login']} ({user['name'] or 'No name'}) - {user['html_url']}\n")
    print(Fore.YELLOW + f"📄 TXT file saved as {filename}")

def export_to_csv(users, filename):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["login", "name", "followers", "following", "html_url"])
        writer.writeheader()
        for user in users:
            writer.writerow(user)
    print(Fore.YELLOW + f"📊 CSV file saved as {filename}")

def unfollow_users(usernames):
    print(Fore.YELLOW + "\n🚫 Unfollowing users...")
    for username in usernames:
        url = f"https://api.github.com/user/following/{username}"
        res = requests.delete(url, headers=headers)
        if res.status_code == 204:
            print(Fore.GREEN + f"✔️ Unfollowed {username}")
        else:
            print(Fore.RED + f"❌ Failed to unfollow {username}: {res.status_code}")

def ask_action():
    print(Fore.GREEN + "\nWhat do you want to do with the users who don't follow you back?")
    print("1. Export as TXT")
    print("2. Export as CSV")
    print("3. Export both TXT and CSV")
    print("4. Unfollow them")
    print("0. Do nothing")
    while True:
        choice = input("Select an option (0-4): ").strip()
        if choice in ["0", "1", "2", "3", "4"]:
            return choice
        else:
            print(Fore.RED + "❌ Invalid option. Please try again.")

def main():
    print_banner()
    
    # Debug print
    print(f"{Fore.CYAN}🔐 USERNAME: {USERNAME}")
    print(f"{Fore.CYAN}🔐 TOKEN: {TOKEN[:4]}********************************{TOKEN[-4:] if TOKEN else ''}")

    print(Fore.GREEN + Style.BRIGHT + "\n🔍 Analyzing your GitHub followers...\n")

    following = set(get_following())
    followers = set(get_followers())
    not_following_back = sorted(following - followers)

    if not not_following_back:
        print(Fore.GREEN + "🎉 Everyone you follow follows you back!")
        return

    print(Fore.YELLOW + f"⏳ Retrieving details for {len(not_following_back)} users who don't follow you back...\n")
    print(Fore.CYAN + "📊 Summary:")
    print(Fore.CYAN + f" - Users you follow: {len(following)}")
    print(Fore.CYAN + f" - Users who follow you: {len(followers)}")
    print(Fore.MAGENTA + f" - Not following you back: {len(not_following_back)}")
    detailed_users = fetch_all_user_details(not_following_back)

    action = ask_action()
    if action == "1":
        export_to_txt(detailed_users, "not_following_back.txt")
    elif action == "2":
        export_to_csv(detailed_users, "not_following_back.csv")
    elif action == "3":
        export_to_txt(detailed_users, "not_following_back.txt")
        export_to_csv(detailed_users, "not_following_back.csv")
    elif action == "4":
        unfollow_users([user["login"] for user in detailed_users])
    else:
        print(Fore.BLUE + "🗂 No action taken.")

if __name__ == "__main__":
    main()
