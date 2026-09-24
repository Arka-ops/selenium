
"""
utils/report_generator.py

Generates:
    1. Excel execution report
    2. Custom HTML execution report
    3. Adds an Excel Download button to pytest-html report

The pytest-html report is modified automatically when it
already exists inside REPORTS_DIR.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from openpyxl import Workbook
from openpyxl.styles import (
    Font,
    PatternFill,
    Alignment,
    Border,
    Side
)

from config.config import REPORTS_DIR


# ================================================================
# COMMON HELPERS
# ================================================================

def _safe_status(result: Dict[str, Any]) -> str:
    """
    Return normalized test status.
    """

    return str(
        result.get(
            "status",
            "SKIP"
        )
    ).upper()


def _get_latest_pytest_html(
    exclude_file: str = ""
) -> str:
    """
    Find the latest HTML report in REPORTS_DIR.

    This is used to locate the pytest-html report
    generated before generate_html_report() is called.
    """

    reports_path = Path(
        REPORTS_DIR
    )

    if not reports_path.exists():
        return ""

    html_files = []

    for file in reports_path.glob("*.html"):

        # Do not select the custom report
        if exclude_file:

            try:

                if (
                    file.resolve()
                    == Path(
                        exclude_file
                    ).resolve()
                ):
                    continue

            except Exception:
                pass

        html_files.append(file)

    if not html_files:
        return ""

    # Latest modified HTML file
    latest = max(
        html_files,
        key=lambda f: f.stat().st_mtime
    )

    return str(latest)


# ================================================================
# EXCEL REPORT GENERATOR
# ================================================================

def generate_excel_report(
    results: List[Dict[str, Any]],
    filepath: str
) -> str:
    """
    Generate a formatted Excel execution report.

    Sheets:
        1. Summary
        2. Execution Report
    """

    workbook = Workbook()

    # ============================================================
    # EXECUTION REPORT SHEET
    # ============================================================

    worksheet = workbook.active
    worksheet.title = "Execution Report"

    headers = [
        "#",
        "Step / Test Case",
        "Status",
        "Result / Message",
        "Duration",
        "Screenshot"
    ]

    worksheet.append(headers)

    # ============================================================
    # STYLES
    # ============================================================

    header_fill = PatternFill(
        fill_type="solid",
        fgColor="16213E"
    )

    header_font = Font(
        bold=True,
        color="FFFFFF",
        size=11
    )

    thin_side = Side(
        style="thin",
        color="D9D9D9"
    )

    border = Border(
        left=thin_side,
        right=thin_side,
        top=thin_side,
        bottom=thin_side
    )

    # ============================================================
    # HEADER STYLE
    # ============================================================

    for cell in worksheet[1]:

        cell.fill = header_fill

        cell.font = header_font

        cell.alignment = Alignment(
            horizontal="center",
            vertical="center"
        )

        cell.border = border

    worksheet.row_dimensions[1].height = 28

    # ============================================================
    # ADD RESULTS
    # ============================================================

    for index, result in enumerate(
        results,
        start=1
    ):

        step = result.get(
            "step",
            f"Step {index}"
        )

        status = _safe_status(
            result
        )

        message = result.get(
            "message",
            "—"
        )

        duration_value = result.get(
            "duration",
            0
        )

        try:

            duration = (
                f"{float(duration_value):.2f}s"
            )

        except (
            TypeError,
            ValueError
        ):

            duration = "—"

        screenshot = result.get(
            "screenshot",
            ""
        )

        worksheet.append([
            index,
            step,
            status,
            message,
            duration,
            screenshot
        ])

    # ============================================================
    # FORMAT CELLS
    # ============================================================

    for row in worksheet.iter_rows(
        min_row=2,
        max_row=worksheet.max_row
    ):

        for cell in row:

            cell.border = border

            cell.alignment = Alignment(
                vertical="top",
                wrap_text=True
            )

    # ============================================================
    # STATUS COLORS
    # ============================================================

    for row in range(
        2,
        worksheet.max_row + 1
    ):

        status_cell = worksheet.cell(
            row=row,
            column=3
        )

        status = str(
            status_cell.value or ""
        ).upper()

        if status == "PASS":

            status_cell.fill = PatternFill(
                fill_type="solid",
                fgColor="C6EFCE"
            )

            status_cell.font = Font(
                bold=True,
                color="006100"
            )

        elif status == "FAIL":

            status_cell.fill = PatternFill(
                fill_type="solid",
                fgColor="FFC7CE"
            )

            status_cell.font = Font(
                bold=True,
                color="9C0006"
            )

        elif status == "SKIP":

            status_cell.fill = PatternFill(
                fill_type="solid",
                fgColor="FFEB9C"
            )

            status_cell.font = Font(
                bold=True,
                color="9C6500"
            )

    # ============================================================
    # SCREENSHOT LINKS
    # ============================================================

    for row in range(
        2,
        worksheet.max_row + 1
    ):

        screenshot_cell = worksheet.cell(
            row=row,
            column=6
        )

        screenshot_path = (
            screenshot_cell.value
        )

        if screenshot_path:

            if os.path.exists(
                str(screenshot_path)
            ):

                screenshot_cell.hyperlink = (
                    str(screenshot_path)
                )

                screenshot_cell.value = (
                    "Open Screenshot"
                )

                screenshot_cell.font = Font(
                    color="0563C1",
                    underline="single"
                )

    # ============================================================
    # FREEZE HEADER
    # ============================================================

    worksheet.freeze_panes = "A2"

    # ============================================================
    # FILTER
    # ============================================================

    if worksheet.max_row >= 2:

        worksheet.auto_filter.ref = (
            worksheet.dimensions
        )

    # ============================================================
    # COLUMN WIDTHS
    # ============================================================

    worksheet.column_dimensions[
        "A"
    ].width = 8

    worksheet.column_dimensions[
        "B"
    ].width = 35

    worksheet.column_dimensions[
        "C"
    ].width = 15

    worksheet.column_dimensions[
        "D"
    ].width = 70

    worksheet.column_dimensions[
        "E"
    ].width = 18

    worksheet.column_dimensions[
        "F"
    ].width = 25

    # ============================================================
    # SUMMARY SHEET
    # ============================================================

    summary = workbook.create_sheet(
        "Summary"
    )

    total = len(results)

    passed = sum(
        1
        for r in results
        if _safe_status(r) == "PASS"
    )

    failed = sum(
        1
        for r in results
        if _safe_status(r) == "FAIL"
    )

    skipped = sum(
        1
        for r in results
        if _safe_status(r) == "SKIP"
    )

    pass_percentage = (
        round(
            passed / total * 100,
            1
        )
        if total
        else 0
    )

    # ============================================================
    # SUMMARY DATA
    # ============================================================

    summary.append([
        "SELENIUM AUTOMATION REPORT",
        ""
    ])

    summary.append([
        "Generated On",
        datetime.now().strftime(
            "%d-%b-%Y %H:%M:%S"
        )
    ])

    summary.append([
        "",
        ""
    ])

    summary.append([
        "Metric",
        "Value"
    ])

    summary.append([
        "Total Steps",
        total
    ])

    summary.append([
        "Passed",
        passed
    ])

    summary.append([
        "Failed",
        failed
    ])

    summary.append([
        "Skipped",
        skipped
    ])

    summary.append([
        "Pass Rate",
        f"{pass_percentage}%"
    ])

    # ============================================================
    # SUMMARY TITLE
    # ============================================================

    summary["A1"].fill = header_fill

    summary["B1"].fill = header_fill

    summary["A1"].font = Font(
        bold=True,
        size=16,
        color="FFFFFF"
    )

    summary["B1"].font = Font(
        bold=True,
        color="FFFFFF"
    )

    # ============================================================
    # SUMMARY TABLE HEADER
    # ============================================================

    for cell in summary[4]:

        cell.fill = header_fill

        cell.font = Font(
            bold=True,
            color="FFFFFF"
        )

        cell.alignment = Alignment(
            horizontal="center"
        )

        cell.border = border

    # ============================================================
    # SUMMARY CELLS
    # ============================================================

    for row in summary.iter_rows():

        for cell in row:

            cell.border = border

            cell.alignment = Alignment(
                vertical="center",
                wrap_text=True
            )

    # ============================================================
    # SUMMARY STATUS COLORS
    # ============================================================

    summary["B6"].fill = PatternFill(
        fill_type="solid",
        fgColor="C6EFCE"
    )

    summary["B7"].fill = PatternFill(
        fill_type="solid",
        fgColor="FFC7CE"
    )

    summary["B8"].fill = PatternFill(
        fill_type="solid",
        fgColor="FFEB9C"
    )

    summary.column_dimensions[
        "A"
    ].width = 28

    summary.column_dimensions[
        "B"
    ].width = 32

    # ============================================================
    # SAVE
    # ============================================================

    workbook.save(
        filepath
    )

    print(
        f"📗 Excel Report generated → "
        f"{filepath}"
    )

    return filepath


# ================================================================
# ADD BUTTON TO PYTEST-HTML REPORT
# ================================================================

def add_excel_button_to_pytest_html(
    pytest_html_path: str,
    excel_path: str
) -> bool:
    """
    Add a visible Excel download button to an
    existing pytest-html report.

    The HTML and Excel files must be in the same
    directory for the relative download link to work.
    """

    html_file = Path(
        pytest_html_path
    )

    excel_file = Path(
        excel_path
    )

    if not html_file.exists():

        print(
            f"⚠️ pytest-html report not found: "
            f"{html_file}"
        )

        return False

    if not excel_file.exists():

        print(
            f"⚠️ Excel report not found: "
            f"{excel_file}"
        )

        return False

    # ============================================================
    # READ HTML
    # ============================================================

    html = html_file.read_text(
        encoding="utf-8"
    )

    # ============================================================
    # PREVENT DUPLICATE BUTTON
    # ============================================================

    marker = (
        "selenium-excel-download-button"
    )

    if marker in html:

        print(
            "ℹ️ Excel download button "
            "already exists."
        )

        return True

    # ============================================================
    # EXCEL FILE NAME
    # ============================================================

    excel_filename = (
        excel_file.name
    )

    # ============================================================
    # BUTTON HTML
    # ============================================================

    button_html = f"""
<!-- =========================================================
     SELENIUM EXCEL DOWNLOAD BUTTON
     ========================================================= -->

<style>

#{marker} {{
    margin: 20px 0;
    padding: 16px 20px;
    background: #f4f6f9;
    border-radius: 8px;
    text-align: right;
    border: 1px solid #e2e6ea;
}}

#{marker} .download-excel-button {{
    display: inline-block;

    background:
        linear-gradient(
            135deg,
            #27ae60,
            #2ecc71
        );

    color: #ffffff !important;

    text-decoration: none !important;

    padding: 12px 22px;

    border-radius: 7px;

    font-family:
        "Segoe UI",
        Arial,
        sans-serif;

    font-size: 14px;

    font-weight: 700;

    cursor: pointer;

    border: none;

    box-shadow:
        0 3px 8px
        rgba(0, 0, 0, 0.15);

    transition:
        all 0.2s ease;
}}

#{marker} .download-excel-button:hover {{
    background:
        linear-gradient(
            135deg,
            #219150,
            #27ae60
        );

    transform:
        translateY(-2px);

    box-shadow:
        0 5px 12px
        rgba(0, 0, 0, 0.20);
}}

#{marker} .download-excel-button:active {{
    transform:
        translateY(0);
}}

</style>

<div id="{marker}">

    <a
        href="{excel_filename}"
        download="{excel_filename}"
        class="download-excel-button"
        title="Download Excel Report"
    >
        📥 Download Excel Report
    </a>

</div>
"""

    # ============================================================
    # INSERTION STRATEGY
    # ============================================================

    inserted = False

    # ------------------------------------------------------------
    # OPTION 1:
    # Directly after pytest-html title
    # ------------------------------------------------------------

    title_end = "</h1>"

    if title_end in html:

        html = html.replace(
            title_end,
            title_end
            + button_html,
            1
        )

        inserted = True

    # ------------------------------------------------------------
    # OPTION 2:
    # After report header
    # ------------------------------------------------------------

    if not inserted:

        environment_header = (
            '<div id="environment-header">'
        )

        if environment_header in html:

            html = html.replace(
                environment_header,
                button_html
                + environment_header,
                1
            )

            inserted = True

    # ------------------------------------------------------------
    # OPTION 3:
    # After body
    # ------------------------------------------------------------

    if not inserted:

        body_tag = "<body>"

        if body_tag in html:

            html = html.replace(
                body_tag,
                body_tag
                + button_html,
                1
            )

            inserted = True

    # ------------------------------------------------------------
    # OPTION 4:
    # Before closing body
    # ------------------------------------------------------------

    if not inserted:

        closing_body = "</body>"

        if closing_body in html:

            html = html.replace(
                closing_body,
                button_html
                + closing_body,
                1
            )

            inserted = True

    # ============================================================
    # SAVE
    # ============================================================

    if inserted:

        html_file.write_text(
            html,
            encoding="utf-8"
        )

        print(
            "✅ Excel download button added "
            "to pytest-html report:"
        )

        print(
            f"   🌐 {html_file}"
        )

        return True

    print(
        "❌ Could not find a suitable "
        "location in pytest-html report."
    )

    return False


# ================================================================
# CUSTOM HTML REPORT
# ================================================================

def generate_html_report(
    results: List[Dict[str, Any]],
    report_title: str =
        "Selenium Capstone – E-Commerce Automation Report"
) -> str:
    """
    Generate the custom HTML report and also modify
    the latest pytest-html report.
    """

    # ============================================================
    # REPORT DIRECTORY
    # ============================================================

    os.makedirs(
        REPORTS_DIR,
        exist_ok=True
    )

    # ============================================================
    # TIMESTAMP
    # ============================================================

    now = datetime.now()

    timestamp = now.strftime(
        "%Y%m%d_%H%M%S"
    )

    # ============================================================
    # FILE PATHS
    # ============================================================

    html_filename = (
        f"execution_report_{timestamp}.html"
    )

    excel_filename = (
        f"execution_report_{timestamp}.xlsx"
    )

    html_filepath = os.path.join(
        REPORTS_DIR,
        html_filename
    )

    excel_filepath = os.path.join(
        REPORTS_DIR,
        excel_filename
    )

    # ============================================================
    # GENERATE EXCEL
    # ============================================================

    generate_excel_report(
        results,
        excel_filepath
    )

    # ============================================================
    # FIND PYTEST-HTML REPORT
    #
    # Do this BEFORE creating our custom HTML,
    # so the pytest report is correctly identified.
    # ============================================================

    pytest_html_path = (
        _get_latest_pytest_html(
            exclude_file=html_filepath
        )
    )

    # ============================================================
    # ADD BUTTON TO PYTEST-HTML
    # ============================================================

    if pytest_html_path:

        add_excel_button_to_pytest_html(
            pytest_html_path,
            excel_filepath
        )

    else:

        print(
            "ℹ️ No existing pytest-html report "
            "found in REPORTS_DIR."
        )

    # ============================================================
    # STATISTICS
    # ============================================================

    total = len(results)

    passed = sum(
        1
        for r in results
        if _safe_status(r) == "PASS"
    )

    failed = sum(
        1
        for r in results
        if _safe_status(r) == "FAIL"
    )

    skipped = sum(
        1
        for r in results
        if _safe_status(r) == "SKIP"
    )

    pass_pct = round(
        (
            passed / total * 100
        )
        if total
        else 0,
        1
    )

    # ============================================================
    # BUILD TABLE
    # ============================================================

    rows_html = ""

    for i, result in enumerate(
        results,
        start=1
    ):

        status = _safe_status(
            result
        )

        color = {
            "PASS": "#2ecc71",
            "FAIL": "#e74c3c",
            "SKIP": "#f39c12"
        }.get(
            status,
            "#95a5a6"
        )

        badge = f"""
        <span style="
            display:inline-block;
            background:{color};
            color:white;
            padding:5px 12px;
            border-radius:20px;
            font-size:12px;
            font-weight:bold;
        ">
            {status}
        </span>
        """

        step = result.get(
            "step",
            f"Step {i}"
        )

        message = result.get(
            "message",
            "—"
        )

        duration_value = result.get(
            "duration",
            0
        )

        try:

            duration = (
                f"{float(duration_value):.2f}s"
            )

        except (
            TypeError,
            ValueError
        ):

            duration = "—"

        screenshot = result.get(
            "screenshot",
            ""
        )

        if (
            screenshot
            and os.path.exists(
                str(screenshot)
            )
        ):

            screenshot_url = (
                "file:///"
                + os.path.abspath(
                    str(screenshot)
                ).replace(
                    "\\",
                    "/"
                )
            )

            ss_link = f"""
            <a
                href="{screenshot_url}"
                target="_blank"
                style="
                    color:#3498db;
                    text-decoration:none;
                "
            >
                🖼️ View Screenshot
            </a>
            """

        else:

            ss_link = "—"

        rows_html += f"""
        <tr>

            <td style="
                padding:12px;
                text-align:center;
                border-bottom:1px solid #eee;
            ">
                {i}
            </td>

            <td style="
                padding:12px;
                border-bottom:1px solid #eee;
                font-weight:500;
            ">
                {step}
            </td>

            <td style="
                padding:12px;
                border-bottom:1px solid #eee;
            ">
                {message}
            </td>

            <td style="
                padding:12px;
                text-align:center;
                border-bottom:1px solid #eee;
            ">
                {duration}
            </td>

            <td style="
                padding:12px;
                text-align:center;
                border-bottom:1px solid #eee;
            ">
                {badge}
            </td>

            <td style="
                padding:12px;
                text-align:center;
                border-bottom:1px solid #eee;
            ">
                {ss_link}
            </td>

        </tr>
        """

    # ============================================================
    # CUSTOM HTML REPORT
    # ============================================================

    html = f"""<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>
    {report_title}
</title>

<style>

* {{
    box-sizing:border-box;
}}

body {{
    margin:0;
    padding:0;

    font-family:
        "Segoe UI",
        Arial,
        sans-serif;

    background:#f4f6f9;

    color:#333;
}}

header {{

    background:
        linear-gradient(
            135deg,
            #1a1a2e,
            #16213e,
            #0f3460
        );

    color:white;

    padding:30px 40px;
}}

header h1 {{
    margin:0 0 8px 0;
    font-size:26px;
}}

header p {{
    margin:0;
    font-size:14px;
    opacity:.8;
}}


/* ============================================================
   DOWNLOAD BUTTON
   ============================================================ */

.download-area {{

    padding:
        20px 40px;

    background:#f4f6f9;

    display:flex;

    justify-content:flex-end;
}}

.download-button {{

    display:inline-block;

    background:
        linear-gradient(
            135deg,
            #27ae60,
            #2ecc71
        );

    color:white;

    text-decoration:none;

    padding:
        13px 24px;

    border-radius:8px;

    font-size:15px;

    font-weight:bold;

    box-shadow:
        0 3px 8px
        rgba(0,0,0,.15);

    transition:
        all .2s ease;
}}

.download-button:hover {{

    background:
        linear-gradient(
            135deg,
            #219150,
            #27ae60
        );

    transform:
        translateY(-2px);

    box-shadow:
        0 5px 12px
        rgba(0,0,0,.20);
}}


/* ============================================================
   SUMMARY
   ============================================================ */

.summary {{

    display:flex;

    gap:16px;

    padding:
        10px 40px 30px;

    flex-wrap:wrap;
}}

.card {{

    background:white;

    border-radius:10px;

    padding:
        20px 28px;

    flex:1;

    min-width:140px;

    text-align:center;

    box-shadow:
        0 2px 8px
        rgba(0,0,0,.08);
}}

.card .num {{

    font-size:32px;

    font-weight:700;
}}

.card .lbl {{

    font-size:13px;

    color:#888;

    margin-top:5px;
}}

.total {{
    color:#3498db;
}}

.pass {{
    color:#2ecc71;
}}

.fail {{
    color:#e74c3c;
}}

.skip {{
    color:#f39c12;
}}

.pct {{
    color:#9b59b6;
}}

.progress-bar-wrap {{

    background:#e0e0e0;

    border-radius:10px;

    height:12px;

    margin-top:10px;

    overflow:hidden;
}}

.progress-bar {{

    background:#2ecc71;

    height:100%;

    width:{pass_pct}%;

    border-radius:10px;
}}


/* ============================================================
   TABLE
   ============================================================ */

.container {{

    padding:
        0 40px 40px;
}}

.table-wrapper {{

    background:white;

    border-radius:10px;

    overflow-x:auto;

    box-shadow:
        0 2px 8px
        rgba(0,0,0,.08);
}}

table {{

    width:100%;

    border-collapse:collapse;

    min-width:900px;
}}

thead {{

    background:
        linear-gradient(
            135deg,
            #0f3460,
            #16213e
        );

    color:white;
}}

th {{

    padding:
        14px 12px;

    text-align:left;

    font-size:13px;
}}

tbody tr:hover {{

    background:#f8fafc;
}}

footer {{

    text-align:center;

    padding:25px;

    font-size:13px;

    color:#999;
}}


/* ============================================================
   MOBILE
   ============================================================ */

@media(max-width:768px) {{

    header {{
        padding:25px 20px;
    }}

    header h1 {{
        font-size:21px;
    }}

    .download-area {{
        padding:20px;
    }}

    .download-button {{
        width:100%;
        text-align:center;
    }}

    .summary {{
        padding:15px 20px 25px;
    }}

    .container {{
        padding:0 20px 30px;
    }}

}}

</style>

</head>


<body>


<!-- =========================================================
     HEADER
     ========================================================= -->

<header>

    <h1>
        🧪 {report_title}
    </h1>

    <p>

        Generated on
        {now.strftime("%d-%b-%Y at %H:%M:%S")}

        &nbsp; | &nbsp;

        Application:
        tutorialsninja.com/demo/

    </p>

</header>


<!-- =========================================================
     DOWNLOAD EXCEL
     ========================================================= -->

<div class="download-area">

    <a
        href="{excel_filename}"
        download="{excel_filename}"
        class="download-button"
    >
        📥 Download Excel Report
    </a>

</div>


<!-- =========================================================
     SUMMARY
     ========================================================= -->

<div class="summary">

    <div class="card">

        <div class="num total">
            {total}
        </div>

        <div class="lbl">
            Total Steps
        </div>

    </div>


    <div class="card">

        <div class="num pass">
            {passed}
        </div>

        <div class="lbl">
            Passed
        </div>

    </div>


    <div class="card">

        <div class="num fail">
            {failed}
        </div>

        <div class="lbl">
            Failed
        </div>

    </div>


    <div class="card">

        <div class="num skip">
            {skipped}
        </div>

        <div class="lbl">
            Skipped
        </div>

    </div>


    <div class="card">

        <div class="num pct">
            {pass_pct}%
        </div>

        <div class="lbl">
            Pass Rate
        </div>

        <div class="progress-bar-wrap">

            <div class="progress-bar"></div>

        </div>

    </div>

</div>


<!-- =========================================================
     EXECUTION RESULTS
     ========================================================= -->

<div class="container">

    <div class="table-wrapper">

        <table>

            <thead>

                <tr>

                    <th>#</th>

                    <th>
                        Step / Test Case
                    </th>

                    <th>
                        Result / Message
                    </th>

                    <th>
                        Duration
                    </th>

                    <th>
                        Status
                    </th>

                    <th>
                        Screenshot
                    </th>

                </tr>

            </thead>

            <tbody>

                {rows_html}

            </tbody>

        </table>

    </div>

</div>


<footer>

    Selenium WebDriver Capstone
    &nbsp; | &nbsp;
    Python Automation Framework

    <br>

    📊 HTML + Excel Execution Report

</footer>


</body>

</html>
"""

    # ============================================================
    # SAVE CUSTOM HTML
    # ============================================================

    with open(
        html_filepath,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(html)

    # ============================================================
    # FINAL OUTPUT
    # ============================================================

    print(
        "\n=================================================="
    )

    print(
        "📊 REPORT GENERATION COMPLETED"
    )

    print(
        "=================================================="
    )

    print(
        f"🌐 Custom HTML : {html_filepath}"
    )

    print(
        f"📗 Excel       : {excel_filepath}"
    )

    if pytest_html_path:

        print(
            f"🧪 pytest-html : {pytest_html_path}"
        )

        print(
            "📥 Excel download button "
            "added to pytest-html report"
        )

    print(
        "==================================================\n"
    )

    return html_filepath

