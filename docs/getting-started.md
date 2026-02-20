# 🚀 Quick Start Guide

This guide will walk you through getting credentials from Bluesky, logging in, and viewing your timeline.

## Step 1: Get an App Password from Bluesky

For security reasons, apcli uses **app passwords** instead of your main Bluesky password. App passwords are special passwords that:

- Can be used by third-party apps
- Can be revoked at any time without changing your main password
- Have limited permissions compared to your main account

### Creating an App Password

1. **Login to Bluesky** - Go to [bsky.app](https://bsky.app) and login with your account
2. **Navigate to Settings** - Click on your profile, then select "Settings"
3. **Go to App Passwords** - In the settings menu, find and click on "App Passwords"
4. **Create New App Password**:
   - Click "Add App Password"
   - Give it a name (e.g., "apcli" or "Terminal CLI")
   - Click "Create"
5. **Copy the Password** - **Important**: Copy the generated password immediately! You won't be able to see it again.

!!! warning "Save Your App Password"
    App passwords are only shown once. Make sure to copy it before closing the dialog. If you lose it, you'll need to create a new one.

!!! tip "Multiple App Passwords"
    You can create multiple app passwords for different apps or devices. This makes it easy to revoke access to a specific app without affecting others.

## Step 2: Login with apcli

Once you have your app password, you can login to apcli:

```bash
uv run apcli login
```

You'll be prompted for:

1. **Handle**: Your Bluesky handle (e.g., `yourname.bsky.social`)
2. **Password**: The **app password** you just created (NOT your main password)

Example:

```bash
$ uv run apcli login
Handle: alice.bsky.social
Password: ****
✓ Successfully logged in as Alice
Session saved to /home/user/.config/apcli/config.json
```

!!! success "Session Saved"
    Your session is saved locally in `~/.config/apcli/config.json`. You only need to login once - the session will persist across commands.

## Step 3: View Your Timeline

Now that you're logged in, you can view your timeline:

```bash
uv run apcli timeline
```

This will display your timeline with:

- Author names
- Post text
- Like counts

### Customize Timeline View

You can control how many posts to show using the `--limit` flag:

```bash
# Show 5 posts
uv run apcli timeline --limit 5

# Show 20 posts
uv run apcli timeline --limit 20

# Show 50 posts
uv run apcli timeline --limit 50
```

Example output:

```
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Author            ┃ Post                                ┃ Likes ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Alice             │ Just discovered this cool CLI tool!│    42 │
│ Bob               │ Beautiful day for coding 🌞         │    15 │
│ Charlie           │ Check out my new project...        │     8 │
└───────────────────┴─────────────────────────────────────┴───────┘

Showing 3 posts
```

## Common Issues

### "Not logged in" Error

If you see this error:

```
✗ Not logged in. Please run 'apcli login' first.
```

Simply run `uv run apcli login` to authenticate.

### "Login failed" Error

This usually means:

1. **Incorrect handle**: Make sure you're using your full handle (e.g., `alice.bsky.social`)
2. **Wrong password**: Remember to use your **app password**, not your main password
3. **Network issues**: Check your internet connection

### "Session may have expired" Error

If your session expires, simply login again:

```bash
uv run apcli login
```

## Security Best Practices

1. **Use App Passwords**: Always use app passwords, never your main password
2. **Revoke Unused Passwords**: Regularly review and revoke app passwords you no longer use
3. **Keep Config Safe**: The config file at `~/.config/apcli/config.json` contains your session. Keep it secure
4. **Don't Share Sessions**: Never share your config file or session string with others

## Next Steps

Now that you're set up, explore the detailed usage guides:

- [Login Command Details](usage-login.md)
- [Timeline Command Details](usage-timeline.md)
