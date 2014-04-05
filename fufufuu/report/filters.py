from fufufuu.report.enums import ReportMangaType


def report_manga_type_display(report_manga_type):
    return ReportMangaType.choices_dict[report_manga_type]
