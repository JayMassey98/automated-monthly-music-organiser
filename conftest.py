"""A collection of Pytest hooks that are used by all test_*.py files.

Outline:
    The only hook that currently exists here is pytest_sessionfinish.
    This hook is used to output the console text from testing main().

References:
    https://docs.pytest.org/en/7.2.x/reference/ for Pytest API info.
"""

# Built-In Libraries
import shutil

# External Libraries
import test_ammo


# Called once all tests are done.
def pytest_sessionfinish():

    # Determine if there is any text from the console.
    output = test_ammo.main_console_output.out.strip()
    error = test_ammo.main_console_output.err.strip()
    
    # Exit if there is no text.
    if not output and not error:
        return

    # Calculate the section title based on the console window.
    columns, rows = shutil.get_terminal_size()
    report_title = ' main console output '
    left_equals_total = ((columns - len(report_title)) - 1) // 2
    right_equals_total = left_equals_total + (columns % 2 != 0)
    report_separator = (f'\n\n{"=" * left_equals_total}'
        + f'{report_title}{"=" * right_equals_total}\n\n')
    
    # Print the captured text.
    report = report_separator
    if output:
        report += output
    if error:
        report += f'\n\nERROR - Script halted with this message:\n{error}'
    print(report, end='')