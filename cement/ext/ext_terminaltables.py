"""
The Terminaltables Extension provides output handling based on the
`Terminaltables <https://pypi.python.org/pypi/terminaltables>`_ library.  It's format is
familiar to users of MySQL, Postgres, etc.
Terminaltables output is similar to Tabulate output but handles a few more
features, such as multi-line cells or tables styling

Requirements
------------

 * Terminaltables (``pip install terminaltables``)


Configuration
-------------

This extension honors the following config settings
under a ``[output.terminaltables]`` section in any configuration file:

    * **style** - Table style, can be ascii, single or double
      (see terminaltables documentation for differences). Default: ascii.

Configurations can be passed as defaults to a CementApp:

.. code-block:: python

    from cement.core.foundation import CementApp
    from cement.utils.misc import init_defaults

    defaults = init_defaults('myapp', 'output.terminaltables')
    defaults['output.terminaltables']['style'] = ascii

    class MyApp(CementApp):
        class Meta:
            label = 'myapp'
            config_defaults = defaults
            extensions = ['terminaltables']
            output_handler = 'terminaltables'

Additionally, an application configuration file might have a section like
the following:

.. code-block:: text

    [myapp]

    # set the cache handler to use
    output_handler = terminaltables


    [output.terminaltables]

    # time in seconds that an item in the cache will expire
    style = ascii


Usage
-----

.. code-block:: python

    from cement.core import foundation
    from cement.utils.misc import init_defaults

    defaults = init_defaults('myapp', 'output.terminaltables')
    defaults['output.terminaltables']['style'] = ascii

    class MyApp(foundation.CementApp):
        class Meta:
            label = 'myapp'
            extensions = ['terminaltables']
            output_handler = 'terminaltables'

    with MyApp() as app:
        app.run()

        # create a dataset
        title = 'Contacts'
        headers = ['NAME', 'AGE', 'ADDRESS']
        data = [
            ["Krystin Bartoletti", 47, "PSC 7591, Box 425\nAPO AP 68379"],
            ["Cris Hegan", 54, "322 Reubin Islands, Leylabury, NC 34388"],
            ["George Champlin", 25, "Unit 6559, Box 124\nDPO AA 25518"],
            ]

        app.render(data, headers=headers, title=title)


Looks like:

.. code-block:: console

    | NAME               | AGE | ADDRESS                                 |
    |--------------------+-----+-----------------------------------------|
    | Krystin Bartoletti |  47 | PSC 7591, Box 425, APO AP 68379         |
    | Cris Hegan         |  54 | 322 Reubin Islands, Leylabury, NC 34388 |
    | George Champlin    |  25 | Unit 6559, Box 124, DPO AA 25518        |

"""

from terminaltables import AsciiTable, SingleTable, DoubleTable
from ..core import output
from ..utils.misc import minimal_logger

LOG = minimal_logger(__name__)


class TerminaltablesOutputHandler(output.CementOutputHandler):

    """
    This class implements the :ref:`IOutput <cement.core.output>`
    interface.  It provides tabularized text output using the
    `Terminaltables <https://pypi.python.org/pypi/terminaltables>`_ module.
    Please see the developer documentation on
    :ref:`Output Handling <dev_output_handling>`.

    **Note** This extension has an external dependency on ``terminaltables``.
    You must include ``terminaltables`` in your applications dependencies
    as Cement explicitly does **not** include external dependencies for
    optional extensions.
    """

    class Meta:

        """Handler meta-data."""

        interface = output.IOutput
        label = 'terminaltables'

        config_defaults = dict(
            style='ascii',
        )

        #: Whether or not to pad the output with an extra pre/post '\n'
        padding = True

        #: Default table format.  See the ``terminaltables`` documentation for
        #: all supported tables formats.
        style = 'ascii'

        #: Table styles map
        style_map = {
            'ascii': AsciiTable,
            'single': SingleTable,
            'double': DoubleTable,
        }

        #: Whether or not to include ``terminaltables`` as an available to choice
        #: to override the ``output_handler`` via command line options.
        overridable = False

    def _config(self, key, default=None):
        """
        This is a simple wrapper, and is equivalent to:
        ``self.app.config.get('output.terminaltables', <key>)``.

        :param key: The key to get a config value from the
         'output.terminaltables' config section.
        :returns: The value of the given key.

        """
        return self.app.config.get(self._meta.config_section, key)

    def render(self, data, headers=[], title=None, **kw):
        """
        Take a data dictionary with optional headers and title and
        render it into a table.  Additional keyword arguments are ignored

        Required Arguments:

        :param table_data: The list of lists to render.
        :returns: str (the rendered template text)

        Optional Arguments:
        :param headers: The table column headers. If absent, the first element
         of the data list will be used

        """
        # title = kw.get('title', self._meta.headers)
        if headers and isinstance(headers, list):
            data.insert(0, headers)

        style = self._config('style', default=self._meta.style)
        tt = self._meta.style_map[style](data, title)

        # Handle custom display settings


        out = tt.table + '\n'

        if self._meta.padding is True:
            out = '\n' + out + '\n'

        return out


def load(app):
    app.handler.register(TerminaltablesOutputHandler)
