# flatpak-pypi
Turns a python requirements.txt file into a flatpak manifest compatible dependency list.

(note: this implementation is in alpha/proof-of-concept state, see "Implementation Notes" below)

### What is flatpak-pypi?

If you ever wanted to ship your app as a [flatpak](https://flatpak.org/),
you probably started by creating a [flatpak manifest](http://docs.flatpak.org/en/latest/flatpak-builder.html#manifests).
And if that app is a python app that depends on a bunch of packages from pypi,
you probably realized it's not that easy to create the list of sources for
your dependencies: you're used to pip doing it for you and you only keep a
list of names and versions, not urls and checksums like flatpak needs.

This is where flatpak-pypi comes to your aid: Instead of having to manually
download every single python package you depend on, note the checksum, and add
it to your manifest, flatpak-pypi automates the process! just give it your
requirements.txt and your flatpak manifest, and it'll do the rest!

### Usage
```./flatpak-pypi.py <requirements_file> <flatpak_manifest>```

flatpak-pypi will modify your manifest, but keep a backup in case it does
something wrong.

Note that at the moment, it doesn't support "updating",
and to prevent duplicate modules it will not modify the json file if it has
all the modules. So if you want to update one of your dependencies, the easiest
thing to do is to remove it from the json manually, and then run flatpak-pypi
again.

### Implementation Notes
The way I implemented this is a bit hacky, because I wanted to get something
working as quickly as possible… so at the moment this creates a virtualenv,
invokes pip in it to download the packages, and then uses the pypi json api
to find the URLs for the packages. This is, of course, awfully inefficient.

A better implementation should parse requirements.txt itself, and use the pypi
json api only, without invoking any subprocesses.

### License
GPLv3+
