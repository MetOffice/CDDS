#!/usr/bin/env python
import sys

from cdds.tests.nightly_tests.setup_task.setup_app import CddsSetupApp


if __name__ == '__main__':
    app = CddsSetupApp(sys.argv[1:])
    app.run()
