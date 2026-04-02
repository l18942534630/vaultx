[app]

title = VaultX
package.name = vaultx
package.domain = org.vaultx

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0

requirements = python3,kivy,cryptography

orientation = portrait
fullscreen = 1

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.archs = arm64-v8a

android.metadata.title = VaultX
android.metadata.versionName = 1.0.0
android.metadata.package = org.vaultx.app

[buildozer]

log_level = 2
warn_on_root = 1

[app:android]

android.api = 31
android.minapi = 21
android.ndk = 26b
android.accept_sdk_license = True

ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
