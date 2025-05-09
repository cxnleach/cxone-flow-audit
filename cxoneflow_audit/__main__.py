import asyncio, logging, os
from asyncio import Semaphore
from docopt import docopt, DocoptExit
from cxoneflow_audit.__version__ import __version__, PROGNAME
from cxoneflow_audit.log import bootstrap
from cxoneflow_audit.util import NameMatcher
from cxoneflow_audit.scm.ado import AdoTool

import requests
# pylint: disable=E1101
requests.packages.urllib3.disable_warnings()

DEFAULT_LOGLEVEL="INFO"

def resolve_from_env(value, env_key):
  if value is not None:
    return value
  elif env_key in os.environ.keys():
    return os.environ[env_key]
  else:
    return None



def common_args(args):
  return {
    "concurrency" : Semaphore(int(args['-t'])),
    "proxy" : { "http" : args['--proxy'], "https" : args['--proxy']} if args['--proxy'] is not None else None,
    "ssl_ignore" : args['-k']
  }


async def main():
  """Usage: cxoneflow-audit [--level LOGLEVEL] [--log-file LOGFILE] [-qk] [-t THREADS] [--proxy PROXY_URL] <scm> [<args>...]
  
  <scm> can be one of:
  adoe                Commands for Azure DevOps
  gh                  Commands for GitHub
  gl                  Commands for Gitlab
  bbdc                Commands for BitBucket Data Center

  Use "cxoneflow-audit help <scm>" for help details for each SCM.

  Runtime Information

  -h,--help           Use this parameter to show help for any command.

  -v,--version        Show version and exit.

  
  Logging Options

  --level LOGLEVEL    Log level [default: INFO]
                      Use: DEBUG, INFO, WARNING, ERROR, CRITICAL
  
  --log-file LOGFILE  A file where logs are written.

  -q                  Do not output logs to the console.

  
  Runtime Options

  -t THREADS         The number of concurrent SCM read/write operations. [Default: 4]
  
  -k                 Ignore SSL verification failures. [Default: False]

  --proxy PROXY_URL  A proxy server to use for communication.
  
  """
                          
  can_log = False
  
  try:

    args = docopt(main.__doc__, version=PROGNAME, options_first = True)

    bootstrap(DEFAULT_LOGLEVEL if args['--level'] is None else args['--level'], 
              not args['-q'], args['--log-file'])
    
    _log = logging.getLogger("main")
    can_log = True
    _log.info(PROGNAME)
    _log.debug(f"{PROGNAME} START")

    result = 1

    main_map = {
      "adoe" : AdoTool(**(common_args(args))),
    }

    scm = args['<scm>']

    if scm in ['help', None]:
      scm = args['<args>'][0] if len(args['<args>']) > 0 else None

      if scm is None:
        scm_list = ",".join(main_map.keys())
        print(f"Please specify one of the following scm names: {scm_list}")
      elif not scm in main_map.keys():
        print(f"{scm} not implemented.")
      else:
        result = await main_map[scm](args['<args>'], True)
    elif scm in main_map.keys():
      result = await main_map[scm](args['<args>'])
    else:
      raise Exception(f"Unknown SCM: {scm}")

    _log.debug(f"{PROGNAME} END with exit code {result}")

    exit (result)
  except DocoptExit as bad_args:
    print("Incorrect arguments provided.")
    print(bad_args)
    exit(1)
  except NotImplementedError as ni:
    if can_log:
      _log.exception(ni)
    else:
      print(f"Not implemented: {ni}")
    exit(1)
  except SystemExit:
    pass
  except BaseException as ex:
    if can_log:
      _log.exception(ex)
    else:
      print(ex)
    exit(1)

if __name__ == "__main__":
  asyncio.run(main())

def cli_entry():
  asyncio.run(main())

