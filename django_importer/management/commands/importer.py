from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--importer', default='', 
                    help='An Importer subclass to use'),
        make_option('--file', default='', 
                    help='The file used for input'),
        make_option('--traceimport', default=False, action='store_true',
                    help='Show traceback of errors during import')
    )
    help = 'Imports a CSV or XML file using an Importer class (django-importer)'

    def import_class(self, cl):
        d = cl.rfind(".")
        classname = cl[d+1:len(cl)]
        m = __import__(cl[0:d], globals(), locals(), [classname])
        return getattr(m, classname)

    def handle(self, *args, **options):
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
            self.stdout.write('\n')
            self.stdout.write('The following errors were found when importing:\n')
            self.stdout.write('--------------------------------------------------------------------------------\n')
            for error in importer.errors:
                self.stderr.write("Line "+str(error['line_num'])+":\n")
                self.stderr.write("--Instance Data: "+str(error['data'])+"\n")
                self.stderr.write("--Exception Message: "+str(error['exception'])+"\n")
                if options['traceimport']:
                    self.stderr.write("--Traceback:\n")
                    self.stderr.write(str(error['traceback']))
                self.stdout.write('--------------------------------------------------------------------------------\n')
            self.stdout.write('\n')
            self.stdout.write('File importing finished successfully with some import errors.\n')
        else:
            self.stdout.write('\n')
            self.stdout.write('File importing finished successfully with no import errors.\n')
