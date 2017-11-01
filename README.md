## Setup

On Windows

```
virtualenv virtualenv
mklink /D virtualenv\Lib\site-packages\gi "C:\Program Files\Python34\Lib\site-packages\gi"
mklink /D virtualenv\Lib\site-packages\cairo "C:\Program Files\Python34\Lib\site-packages\cairo"
mklink /D virtualenv\Lib\site-packages\gnome "C:\Program Files\Python34\Lib\site-packages\gnome"
mklink /D virtualenv\Lib\site-packages\pydbus "C:\Program Files\Python34\Lib\site-packages\pydbus"
mklink /D virtualenv\Lib\site-packages\pygtkcompat "C:\Program Files\Python34\Lib\site-packages\pygtkcompat"
mklink virtualenv\Lib\site-packages\rpath.pth "C:\Program Files\Python34\Lib\site-packages\rpath.pth"
```

```
pip install Markdown pymdown-extensions cyrusbus
```