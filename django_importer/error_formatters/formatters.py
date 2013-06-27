

class ErrorFormatter(object):
    pre_errors_message = 'The following errors were found when importing:'
    post_errors_message = 'File importing finished successfully with some import errors.'

    def __init__(self, field_map=None):
        self.field_map = field_map or {}

    def format_error(self, error, importer_options):
        raise NotImplementedError

    def get_field_name(self, field):
        return self.field_map.get(field, field)

    def show_instance_data(self, data):
        instance_data = '{%s }'

        field_list = []
        for field in data:
            field_name = self.get_field_name(field)

            output_data = data[field]
            for data_transformer in self.data_transformers():
                output_data = data_transformer(self, output_data)

            field_text = " %s: %s" % (field_name, output_data)
            field_list.append(field_text)

        return instance_data % ','.join(field_list)

    def data_transformers(self):
        return [getattr(self.__class__, method) for method in dir(self.__class__) if method.startswith('transform_')]


class DefaultErrorFormatter(ErrorFormatter):
    def format_error(self, error, importer_options):
        error_output = ''

        error_output += "Line "+str(error['line_num'])+":\n"
        error_output += "--Instance Data: "+str(error['data'])+"\n"
        error_output += "--Exception Message: "+str(error['exception'])+"\n"

        if importer_options['traceimport']:
            error_output += "--Traceback:\n"
            error_output += str(error['traceback'])

        return error_output
