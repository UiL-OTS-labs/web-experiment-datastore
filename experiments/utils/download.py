import csv
import io
import zipfile
import json

from django.http import FileResponse, HttpResponse
from django.utils.datastructures import OrderedSet

from experiments.models import DataPoint, Experiment


EXPORT_REPORT_HEADER = """EXPORT REPORT

This file contains a list of all files in this experiment.

It also indicates if the file was successfully added or not. If a file could 
not be added, you can look at the raw file to see what caused it to fail.

Files:

"""


def create_download_response_zip(file_format: str, experiment: Experiment) -> \
        FileResponse:

    if file_format == 'raw':
        zip_file = _create_zip(
            experiment,
            lambda dp: str(dp.pk) + '.txt',
            lambda dp: dp.data
        )
    else:
        zip_file = _create_zip(
            experiment,
            lambda dp: str(dp.pk) + '.csv',
            lambda dp: _flatten_json(dp.data)
        )

    # Reset the buffer cursor to the start, so FileResponse reads the entire
    # buffer
    zip_file.seek(0)

    return FileResponse(
        zip_file,
        filename="{}-{}.zip".format(experiment.title, file_format)
    )


def create_file_response_single(file_format: str, data_point: DataPoint) -> \
        HttpResponse:

    try:
        if file_format == 'raw':
            data = data_point.data
            file_format = 'txt'
            content_type = "text/plain"
        else:
            data = _flatten_json(data_point.data)
            content_type = "text/csv"
    except:
        data = "Sorry, your file could not be exported. Try looking at the " \
               "raw file to see what could mess up any conversion."
        content_type = "text/plain"
        file_format = 'txt'

    response = HttpResponse(
        data,
        content_type=content_type,
    )

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

    return buffer


def _flatten_json(data: str) -> str:
    json_data = json.loads(data)

    columns = OrderedSet()

    if not isinstance(json_data, list):
        json_data = [json_data]

    for el in json_data:
        if isinstance(el, dict):
            for key in el.keys():
                columns.add(key)

    buffer = io.StringIO()
    csw_writer = csv.DictWriter(buffer, columns, extrasaction='ignore')

    csw_writer.writeheader()
    csw_writer.writerows(json_data)

    buffer.seek(0)
    output = buffer.read()
    buffer.close()

    return output
