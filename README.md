# Flask + Sapo Ink

Bootstrap your [Flask][1] webapp, by quickly and easily integrating [SAPO Ink][2]. It includes all the base CSS/Javascript required for you to start developing slick, elegant and responsive websites.

Besides providing a very limited set of functionalities, the code is in a **VERY EARLY STAGE** and I would not encourage you to use it, unless you know what you're doing.

This came to existence as a side-project to something I'm doing in my spare time, so I expect to improve it within the next couple of weeks (as the necessity arises, I'll try to develop solutions abstract enough to also fit here). If you want to pitch in, you're absolutely free to do so. :)


## Installation

The easiest way to use the package, would be to install it via [pip][3]:

```
pip install git+https://github.com/diogoosorio/flask-sapo-ink.git@master#egg=flask_ink
```

After that, you just have to load the extension when you initialize your application:

```python
from flask import Flask
from flask_ink import Ink

def create_app():
    app = Flask(__name__)
    Ink(app)
    
    return app

if __name__ == '__main__':
    create_app().run()
```

You will then be able to extend the [base.html](flask_ink/templates/ink/base.html) file provided by the extension:

```
{% extends "ink/base.html" %}
```

See the template's [available blocks](#available-blocks) for information on what you may change.

It's also worth mentioning that pretty much all the CSS and Javascript files that are bundled within Ink are included. I've also created an helper function that you may call
within your template files to include static assets that are shipped with Ink.

To load [Ink's Modal javascript library][5] you could simply do this within your template:

```python
{% extends "ink/base.html" %}
{% block scripts %}
{{super()}}
<script src="{{ink_load_asset('js/ink.modal.js')}}"></script>
{% endblock scripts %}
```

## Available Blocks

- **document** - the whole document. Declared on the top of the template.
- **html_attributes** - <html> tag attributes.
- **html** - declared after the <html> tag.
- **head** - declared after the <head> tag.
- **title** - the page title.
- **metas** - declared within the header. All your page's meta should go in here.
- **styles** - declared within the header.
- **body_attributes** - <body> tag attributes.
- **body** - the document's body.
- **nav_bar** - top navigation bar. Wrapped within a div with 'ink-grid' as its class.
- **content** - the page's content.
- **scripts** - javascript files to be loaded right at the end of the page

Take a peek at the [base.html](flask_ink/templates/ink/base.html) file for more information.


## Configuration options

For your convenience, the extension will take in account a set of configuration parameters:

```python
INK_MINIFIED_ASSETS = True  # Append a .min to the js/css files (ink.css -> ink.min.css)
INK_VERSION = '2.2.1' # Used to obtain the correct files from Sapo's CDN and by the INK_ASSET_APPEND_VERSION_QUERYSTRING
INK_DEFAULT_ASSET_LOCATION = 'sapo' # Use Sapo's CDN to serve the files by default. 'local' to serve them from your app.
INK_QUERYSTRING_VERSION = True # Append a ?v={version_number} when incuding the files
```
You can add these configuration parameters like you would [add any other configuration to your Flask app][4].


## Roadmap

* Delegate the responsibility of handling the "minify" parameter to the AssetLocation instance (i.e. there are no conventions on the framework -> ink.min.js | ink-min.css).

* Add an abstraction layer to the SapoCDN class. It would be nice to be able to create an instance that represents any CDN.

* Extend the base.html template. Not even a fotter? Really?

* Add some template helpers/partials for the most common widgets used by Ink (calendar, progress, modal, ...).


[1]: http://flask.pocoo.org/
[2]: http://ink.sapo.pt
[3]: http://www.pip-installer.org/en/latest/
[4]: http://flask.pocoo.org/docs/config/
[5]: http://ink.sapo.pt/js/ui#modal
