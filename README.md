
# 🐙 GitHub Follower Tracker

![Banner](images/banner.jpg)

**GitHub Follower Tracker** is a fast and interactive Python tool that checks which GitHub users you follow that don’t follow you back. It features animated terminal spinners, optional export to TXT/CSV, parallel requests for speed, and colorful CLI output. Ideal for managing your GitHub social connections in style.

---

## 🚀 Features

- Identify users who don’t follow you back
- Export results to `.txt` and/or `.csv`
- Parallel data fetching for performance
- ASCII GitHub logo and spinner animations
- Environment-based secure configuration

---

## ⚙️ Configuration

To run the script, you **must create and configure a [`.env.local`](https://github.com/marichu-kt/GitHub-Unfollowed/blob/main/.env.local) file** in the root of the project with the content:

```env
GITHUB_USERNAME=XXXXXXXXXXXXXXXXXXX
GITHUB_TOKEN=XXXXXXXXXXXXXXXXXXX
```

Replace `XXXXXXXXXXXXXXXXXXX` with:

- `GITHUB_USERNAME`: your GitHub username
- `GITHUB_TOKEN`: your personal access token from [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)

---

## 📁 Output Files

- `not_following_back.txt`: Plain list with GitHub usernames and profile URLs
- `not_following_back.csv`: Detailed list including name, bio, followers, etc.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE) — free to use, modify, and distribute.
