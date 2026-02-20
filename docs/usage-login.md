# 🔐 Login Command

The `login` command authenticates you with Bluesky and saves your session for future use.

## Basic Usage

```bash
atpcli bsky login
```

This will prompt you for your credentials interactively.

## Command Options

```bash
atpcli bsky login [OPTIONS]
```

### Options

- `--handle TEXT`: Your Bluesky handle (optional, will prompt if not provided)
- `--password TEXT`: Your app password (optional, will prompt if not provided)
- `--help`: Show help message

## Interactive Mode

When you run the command without options, you'll be prompted:

```bash
$ atpcli bsky login
Handle: alice.bsky.social
Password: ****
✓ Successfully logged in as Alice
Session saved to /home/user/.config/atpcli/config.json
```

!!! tip "Password Hidden"
    The password input is hidden for security. You won't see characters as you type.

## Providing Credentials as Options

You can provide credentials as command-line options:

```bash
atpcli bsky login --handle alice.bsky.social --password your-app-password
```

!!! warning "Security Risk"
    Providing passwords on the command line can expose them in shell history. Interactive mode is recommended.

## Session Storage

When you login, atpcli saves your session to:

```
~/.config/atpcli/config.json
```

This file contains:

- Your handle
- Session authentication string

The session persists across commands, so you only need to login once.

## Session File Format

The config file is a simple JSON file:

```json
{
  "handle": "alice.bsky.social",
  "session": "eyJ...session-string...xyz"
}
```

## Re-authentication

To login with a different account, simply run `login` again:

```bash
atpcli bsky login
```

This will overwrite the previous session.

## Troubleshooting

### Invalid Credentials

If login fails with invalid credentials:

1. **Check your handle**: Use your full handle (e.g., `alice.bsky.social`)
2. **Verify app password**: Make sure you're using an app password, not your main password
3. **Create new app password**: If you've lost your app password, create a new one

### Network Errors

If you see network-related errors:

1. Check your internet connection
2. Verify Bluesky services are available
3. Check for firewall or proxy issues

### Permission Errors

If you get permission errors when saving the config:

```bash
# Ensure the config directory exists and is writable
mkdir -p ~/.config/atpcli
chmod 755 ~/.config/atpcli
```

## Security Considerations

### App Passwords vs Main Password

**Always use app passwords**, never your main Bluesky password:

- ✅ **App passwords** are safer and can be revoked
- ✅ App passwords have limited permissions
- ✅ Multiple app passwords can be created for different apps
- ❌ **Main passwords** give full account access
- ❌ Main passwords can't be revoked without changing them

### Session Security

Your session file contains authentication credentials. Protect it:

- Keep `~/.config/atpcli/config.json` private
- Don't share the file with others
- Don't commit it to version control
- Set appropriate file permissions: `chmod 600 ~/.config/atpcli/config.json`

### Revoking Access

To revoke atpcli's access:

1. Go to Bluesky Settings → App Passwords
2. Find the app password you created for atpcli
3. Click "Revoke"
4. Delete `~/.config/atpcli/config.json` on your machine

## Examples

### First-time Login

```bash
$ atpcli bsky login
Handle: alice.bsky.social
Password: ****
✓ Successfully logged in as Alice
Session saved to /home/alice/.config/atpcli/config.json
```

### Switching Accounts

```bash
$ atpcli bsky login
Handle: bob.bsky.social
Password: ****
✓ Successfully logged in as Bob
Session saved to /home/user/.config/atpcli/config.json
```

### Login with Command-line Options

```bash
$ atpcli bsky login --handle alice.bsky.social --password xxxx-xxxx-xxxx-xxxx
✓ Successfully logged in as Alice
Session saved to /home/alice/.config/atpcli/config.json
```
