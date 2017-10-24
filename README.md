# isaw.id

Manage opaque, unique ids for ISAW entities within multiple arbitrary namespaces.

## Usage

```python
from isaw.id import Maker

m = Maker(
    namespace='inscriptions',
    registry_path='/path/to/isaw-id-registry-dir')
with open('my-project/texts/733.xml', 'r') as f:
    content = f.read()
this_id = m.make(content=content)
print(repr(this_id))
'/inscriptions/7cd44e'
```

wherein:
 - ```namespace``` is an arbitrary string
 - ```registry_path``` is a filesystem path to a directory containing a textfile with the same name as the value in ```namespace``` (the "namespace register")
 - the ```content``` argument to ```Maker.make()``` is any Python data object, including a zero-length string, that can be successfully converted to a sequence of bytes using ```bytes()```.

The namespace register is a text file containing a newline-delimited list of unique ids previously generated against the namespace whose title it bears. Any newly generated ID is checked by ```Maker.make()``` against this list to ensure uniqueness unless the optional ```ensure_unique``` argument to the ```Maker``` class constructor is set to ```False```. Newly generated ids are written to the namespace register when a ```Maker``` instance is torn down.

For additional optional arguments and usage examples, see the docstrings in ```isaw/id/__init__.py``` and the tests in ```tests/test_id.py```.
