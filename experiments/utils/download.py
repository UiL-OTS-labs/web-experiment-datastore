import csv
import io
import zipfile
import json

from django.http import FileResponse, HttpResponse
from django.utils.datastructures import OrderedSet

from experiments.models import DataPoint, Experiment

EXPORT_NO_VALUE = "NA"

EXPORT_REPORT_HEADER = """EXPORT REPORT

This file contains a list of all files in this experiment.

It also indicates if the file was successfully added or not. If a file could 
not be added, you can look at the raw file to see what caused it to fail.

Files:

"""


def create_download_response_zip(file_format: str, experiment: Experiment) -> \
        FileResponse:
    """Creates a FileResponse containing a ZIP with all data of the provided
    experiment, in the desired format. """

    # Create the zip using the desired methods
    if file_format == 'raw':
        zip_file = _create_zip(
            experiment,
            lambda dp: str(dp.number) + '.txt',
            # Raw should just return the data of the DataPoint
            lambda dp: dp.data
        )
    else:
        zip_file = _create_zip(
            experiment,
            lambda dp: str(dp.number) + '.csv',
            # CSV should apply _flatten_json to the data and return the result
            lambda dp: _flatten_json(dp.data)
        )


    return FileResponse(
        zip_file,
        filename="{}-{}.zip".format(experiment.title, file_format)
    )


def create_file_response_single(file_format: str, data_point: DataPoint) -> \
        HttpResponse:
    """Creates a HttpResponse containing a the data of the provided
    DataPoint, in the desired format. """

    try:
        if file_format == 'raw':
            data = data_point.data
            # Rewrite file_format to txt, as it will be used as the file
            # extension
            file_format = 'txt'
            content_type = "text/plain"
        else:
            data = _flatten_json(data_point.data)
            content_type = "text/csv"
    except:
        # In case of any errors, provide a file that says sorry
        data = "Sorry, your file could not be exported. Try looking at the " \
               "raw file to see what could mess up any conversion."
        content_type = "text/plain"
        file_format = 'txt'

    response = HttpResponse(
        data,
        content_type=content_type,
    )

    # Set the content disposition header, so that browser see the page as a
    # downloadable file
    filename = "{}-{}.{}".format(
        data_point.experiment.title,
        data_point.pk,
        file_format
    )
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)

    return response


def _create_zip(
        experiment: Experiment,
        filename_generator: callable,
        processor: callable
) -> io.BytesIO:
    """Creates a ZIP in a BytesIO buffer.

    :param experiment: The experiment containing the requested data
    :param filename_generator: a callable that provides a filename when given a
    datapoint object
    :param processor: a callable that produces the data in the intended
    format when given a datapoint object
    """
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "a", zipfile.ZIP_DEFLATED, True) as zip_file:
        export_report = EXPORT_REPORT_HEADER

        for dataPoint in experiment.datapoint_set.all():
            filename = filename_generator(dataPoint)
            try:
                data = processor(dataPoint)
                zip_file.writestr(filename, data)
                export_report += "-{} - SUCCESS\n".format(filename)
            except Exception as e:
                export_report += "-{} - FAILED\n".format(filename)

        zip_file.writestr("export_report.txt", export_report)

    # Reset the buffer cursor to the start, so FileResponse reads the entire
    # buffer
    buffer.seek(0)

    return buffer


def _flatten_json(data: str) -> str:
    """Flattens a JSON *string* into a CSV string"""
    json_data = json.loads(data)

    # Ordered set, so we preserve the order
    columns = OrderedSet()

    # If it is not a list, set the data in list so the next code doesn't
    # do weird stuff
    if not isinstance(json_data, list):
        json_data = [json_data]

    for el in json_data:
        # It should be a dict
        if isinstance(el, dict):
            for key in el.keys():
                # Always add the key, even if the value is empty (checked
                # later on). The column itself should at least be included
                columns.add(key)

                # If this key has no/an empty value, we want to print NA instead
                # However, the DictWriter only adds NA if the field is missing
                # So, we set it to NA manually
                if not el[key]:
                    el[key] = EXPORT_NO_VALUE

    buffer = io.StringIO()
    # DictWriter writes a dict into a CSV, only including the columns given.
    # In addition, extrasaction is set to ignore to keep it from raising
    # exceptions when it encounters an unknown column.
    csw_writer = csv.DictWriter(
        buffer,
        columns,
        extrasaction='ignore',
        restval=EXPORT_NO_VALUE,
    )

    csw_writer.writeheader()
    csw_writer.writerows(json_data)

    # Read the output from the buffer
    buffer.seek(0)
    output = buffer.read()
    buffer.close()

    return output
