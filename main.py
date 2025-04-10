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

# Load environment variables from .env.local
load_dotenv(dotenv_path=".env.local")
USERNAME = os.getenv("GITHUB_USERNAME")
TOKEN = os.getenv("GITHUB_TOKEN")

# Validate credentials
if not USERNAME or not TOKEN:
    print(Fore.RED + "❌ Error: GITHUB_USERNAME or GITHUB_TOKEN not set in .env.local")
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
            "bio": data.get("bio"),
            "followers": data.get("followers"),
            "following": data.get("following"),
            "html_url": data.get("html_url"),
            "type": data.get("type")
        }
    else:
        return {
            "login": username,
            "name": "",
            "bio": "",
            "followers": "",
            "following": "",
            "html_url": "",
            "type": "User"
        }

def ask_export_format():
    print(Fore.GREEN + "\nIn which format do you want to export the results?")
    print("0. Do not export")
    print("1. TXT")
    print("2. CSV")
    print("3. Both")
    while True:
        choice = input("Select an option (0-3): ").strip()
        if choice == "":
            print(Fore.YELLOW + "ℹ️  No file will be exported.")
            return "none"
        elif choice in ["0", "1", "2", "3"]:
            return choice
        else:
            print(Fore.RED + "❌ Invalid option. Please try again.")

def export_to_txt(users, filename):
    with open(filename, "w", encoding="utf-8") as f:
        for user in users:
            f.write(f"{user['login']} ({user['name'] or 'No name'}): {user['html_url']}\n")
    print(Fore.YELLOW + f"📄 TXT file saved as {filename}")

def export_to_csv(users, filename):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["login", "name", "type", "bio", "followers", "following", "html_url"])
        writer.writeheader()
        for user in users:
            writer.writerow(user)
    print(Fore.YELLOW + f"📊 CSV file saved as {filename}")

def fetch_all_user_details(usernames, max_workers=10):
    detailed_users = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(get_user_details, user): user for user in usernames}
        for future in as_completed(futures):
            try:
                user_info = future.result()
                login = f"{user_info['login']:<20}"
                name = f"{user_info['name'] or 'No name':<25}"
                print(Fore.RED + f"{login} - {name}")
                detailed_users.append(user_info)
            except Exception as e:
                print(Fore.RED + f"⚠️  Error retrieving user data: {e}")
    return detailed_users

def main():
    print_banner()
    print(Fore.GREEN + Style.BRIGHT + "\n🔍 Analyzing your GitHub followers...\n")

    following = set(get_following())
    followers = set(get_followers())
    not_following_back = sorted(following - followers)

    if not not_following_back:
        print(Fore.GREEN + "🎉 Everyone you follow follows you back!")
        return

    print(Fore.MAGENTA + f"\n👥 Users you follow who do NOT follow you back ({len(not_following_back)}):")
    print(Fore.YELLOW + f"⏳ Retrieving details for {len(not_following_back)} users...\n")

    detailed_users = fetch_all_user_details(not_following_back)

    option = ask_export_format()
    if option == "1":
        export_to_txt(detailed_users, "not_following_back.txt")
    elif option == "2":
        export_to_csv(detailed_users, "not_following_back.csv")
    elif option == "3":
        export_to_txt(detailed_users, "not_following_back.txt")
        export_to_csv(detailed_users, "not_following_back.csv")
    else:
        print(Fore.BLUE + "🗂 No file was exported.")

    print(Fore.CYAN + "\n📊 Summary:")
    print(Fore.CYAN + f" - Users you follow: {len(following)}")
    print(Fore.CYAN + f" - Users who follow you: {len(followers)}")
    print(Fore.MAGENTA + f" - Not following you back: {len(not_following_back)}")

if __name__ == "__main__":
    main()
