# Setting Up My Password-Protected Website Using Vim

## 1. Create/Edit `index.html` in `public_html`

```bash
cd ~/public_html
vim index.html
```

### Vim Commands:
- Press `i` to enter INSERT mode.
- Type my HTML content:

```html
Anyone can view this page.
<p>
<a href="secret">Password-protected directory</a>
```

- Press `ESC` to exit INSERT mode.
- Save and exit: Type `:wq` and press `Enter`.

## 2. Create the `secret` Directory

```bash
mkdir ~/public_html/secret
cd ~/public_html/secret
```

## 3. Create `index.html` in the `secret` Directory

```bash
vim index.html
```

### Add Content:

Press `i` to insert:

```html
<h1>Secret Page</h1>
<img src="myimage.png" width="500">
<p>This page is password-protected.</p>
```

- Save and exit: `ESC → :wq → Enter`.

## 4. Upload My Image to the `secret` Directory

From my local machine (not the server), run:

```bash
scp /path/to/local/myimage.png myusername@myserver.net:~/public_html/secret/
```

Replace `/path/to/local/myimage.png` with the actual path to my image.

## 5. Set Permissions

```bash
chmod 750 ~  # Allow the web server to access my home directory
chmod 755 ~/public_html  # Make the public directory accessible
```

## 6. Create `.htaccess` for Password Protection

```bash
cd ~/public_html/secret
vim .htaccess
```

### Add This Content:

```apache
<Limit GET POST>
Require valid-user
</Limit>

AuthType Basic
AuthName "Secret Directory"
AuthUserFile "/home/myusername/public_html/secret/.htpasswd"
```

- Save and exit `(:wq)`.

## 7. Create the Password File (`.htpasswd`)

```bash
htpasswd -c .htpasswd myusername
```

Replace `myusername` with the username I want.
Enter a password when prompted (e.g., `mypassword123`).

## 8. Verify Permissions

```bash
ls -ld ~  # Should show drwxr-x---
ls -la ~/public_html/secret  # Ensure .htaccess and .htpasswd exist
```

## 9. Test My Website

- **Public page:** [http://myserver.net/~myusername/](http://myserver.net/~myusername/)
- **Secret page:** [http://myserver.net/~myusername/secret/](http://myserver.net/~myusername/secret/)

I should see a password prompt for the secret page.

## Troubleshooting

### Permission Issues:

```bash
chmod 644 ~/public_html/secret/.htaccess  # If the server can't read it
chmod 644 ~/public_html/secret/.htpasswd
```

### Broken Image:
- Double-check the filename in `index.html` matches the uploaded image.
- Verify the image is in `~/public_html/secret/`.

## Notes
- I should remember to send the password I set for `myusername` to the relevant contact if needed.

## Vim Cheat Sheet

| Action | Command |
|--------|---------|
| Edit a file | `vim filename` |
| Insert text | Press `i` |
| Save and quit | `ESC → :wq → Enter` |
| Quit without saving | `ESC → :q! → Enter` |
| Delete a line | `ESC → dd` |

Let me know if I get stuck! 😊
