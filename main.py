import argparse
import inspect
import logging
from importlib import import_module

DEFAULT_FORMATTER = '%(asctime)s[%(filename)s:%(lineno)d][%(levelname)s]:%(message)s'
logging.basicConfig(format=DEFAULT_FORMATTER, level=logging.INFO)


def script_main(params):
    client = params.get('client')
    m = import_module('.'.join(['clients', client]))
    for name, obj in inspect.getmembers(m):
        if inspect.isclass(obj) and str(obj).find('clients') != -1:
            instance = obj()
            instance.before_run(**params)
            instance.run(**params)
            break


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--client', required=True)
    parser.add_argument('-u', '--username')
    parser.add_argument('-p', '--password')
    parser.add_argument('--cookie')
    args = parser.parse_args()
    return script_main(vars(args))


if __name__ == '__main__':
    main()
