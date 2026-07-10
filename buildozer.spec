[app]

# (string) Title of your application
title = Master's Scholarship

# (string) Package name
package.name = mastersscholarship

# (string) Package domain (needed for android packaging)
package.domain = org.sulaiman

# (string) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,db

# (string) Application version
version = 0.1

# (list) Application requirements
# Yahan humne kivymd aur sqlite3 specify kiya hai taake ye android me include hon
requirements = python3==3.11,kivy==2.3.0,kivymd==1.2.0,plyer

# (str) Supported orientations (landscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
# Agar baad me push notification automatic chalani ho to permissions chahiye hoti hain
android.permissions = INTERNET, WAKE_LOCK, RECEIVE_BOOT_COMPLETED

# (int) Android API to use
android.api = 33

# (int) Minimum API required
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 27b

# (bool) Use Gradle instead of Ant
android.gradle_dependencies = 

# (bool) Enable AndroidX support (required for KivyMD)
android.enable_androidx = True

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
