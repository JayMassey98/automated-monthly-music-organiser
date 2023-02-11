"""A collection of Pytest fixtures that are used by test_*.py files.

Outline:
    The only fixture that currently exist is 'pytest_sessionfinish'.
    This fixture is used to output the console from testing main().

References:
    https://docs.pytest.org/en/7.2.x/reference/ for Pytest API info.
"""

# External Libraries
import test_ammo


# Pytest calls this once all its tests are done.
def pytest_sessionfinish(session, exitstatus):

    # Determine if there was any console output.
    if test_ammo.main_console_output.out[:-1]:

        # Add a section on the end of the report.
        print('\n\n============================='
              + ' main console output '
              + '=============================\n')
    
        # Print the captured output from main() in test_ammo.py.
        print(test_ammo.main_console_output.out[:-1], end='')

    # If any errors were captured, print them.
    if test_ammo.main_console_output.err[:-1]:
        print('\n\nScript halted with the following error:\n'
              + error, end='')