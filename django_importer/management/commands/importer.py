from optparse import make_option

from django.core.management.base import BaseCommand
from django.utils import translation
from django_importer.error_formatters.formatters import DefaultErrorFormatter
from django.conf import settings


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--importer', default='', 
                    help='An Importer subclass to use'),
        make_option('--file', default='', 
                    help='The file used for input'),
        make_option('--traceimport', default=False, action='store_true',
                    help='Show traceback of errors during import'),
        make_option('--errorformatter', default=None,
                    help='An ErrorFormatter subclass to show errors')

    )
    help = 'Imports a CSV or XML file using an Importer class (django-importer)'
    can_import_settings = True

    def import_class(self, cl):
        d = cl.rfind(".")
        classname = cl[d+1:len(cl)]
        m = __import__(cl[0:d], globals(), locals(), [classname])
        return getattr(m, classname)

    def get_error_formatter(self, options, importer):
        error_formatter_class = options.get("errorformatter", None)

        if importer.field_map:
            field_map = importer.field_map

        if error_formatter_class:
            error_formatter = self.import_class(error_formatter_class)

            return error_formatter(field_map)

        return DefaultErrorFormatter(field_map)

    def handle(self, *args, **options):
        translation.activate(settings.LANGUAGE_CODE)

        class_name = options.get("importer", None)
        file = options.get("file", None)
        if not class_name or not file:
            self.stderr.write('Error: The --importer and --file parameters are required!\n')
            return
        imported_class = self.import_class(class_name)
        importer = imported_class(file)
        self.stdout.write('Importing the file...\n')
        importer.parse()

        if importer.errors:
            error_formatter = self.get_error_formatter(options, importer)

            self.stdout.write('\n')
            self.stdout.write(error_formatter.pre_errors_message)
            self.stdout.write('\n')
            self.stdout.write('--------------------------------------------------------------------------------\n\n')

            for error in importer.errors:
                self.stdout.write(error_formatter.format_error(error, options))
                self.stdout.write('\n\n')
                self.stdout.write('--------------------------------------------------------------------------------')
                self.stdout.write('\n\n')

            self.stdout.write('\n')
            self.stdout.write(error_formatter.post_errors_message)
            self.stdout.write('\n')
        else:
            self.stdout.write('\n')
            self.stdout.write('File importing finished successfully with no import errors.\n')

        translation.deactivate()


