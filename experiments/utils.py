import csv
import io
import zipfile
import json

from django.http import FileResponse, HttpResponse
from django.utils.datastructures import OrderedSet

from experiments.models import DataPoint, Experiment


def create_download_response_zip(file_format: str, experiment: Experiment) -> \
        FileResponse:

    if file_format == 'raw':
        zip_file = _create_zip(
            experiment,
            lambda dp, zf: zf.writestr(
                str(dp.pk) + '.txt',
                dp.data
            )
        )
    else:
        zip_file = _create_zip(
            experiment,
            lambda dp, zf: zf.writestr(
                str(dp.pk) + '.csv',
                _flatten_json(dp.data).read()
            )
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

    if file_format == 'raw':
        data = data_point.data
        file_format = 'txt'
        content_type = "text/plain"
    else:
        data = _flatten_json(data_point.data)
        content_type = "text/csv"

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


def _create_zip(experiment: Experiment, processor: callable) -> io.BytesIO:
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "a", zipfile.ZIP_DEFLATED, True) as zip_file:
        for dataPoint in experiment.datapoint_set.all():
            processor(dataPoint, zip_file)

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
