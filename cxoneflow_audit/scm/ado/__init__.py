from cxoneflow_audit.scm.ado.ado_auditor import AdoAuditor
from cxoneflow_audit.scm.ado.ado_deployer import AdoDeployer
from cxoneflow_audit.scm.ado.ado_remover import AdoRemover
from cxoneflow_audit.scm.ado.ado_kicker import AdoKicker
from typing import List
from docopt import docopt
from cxoneflow_audit.scm.common import SCMTool


class AdoTool(SCMTool):

  def __init__(self, **kwargs):
     super().__init__(audit=self.ado_audit, deploy=self.ado_deploy, remove=self.ado_remove, kickoff=self.ado_kickoff, **kwargs)

  async def ado_audit(self, ado_args : List[str], help : bool = False):
    """Usage: cxoneflow-audit adoe audit [--no-config] [--outfile CSVFILE] 
                      [--match-regex M_REGEX | --skip-regex S_REGEX]
                      (--pat PAT | --pat-env) (--scm-url URL)
                      (--cx-url CX_URL) TARGETS...
    
    TARGETS...                  One or more collection names where containing projects
                                where service hook configurations will be audited.

    Deployment Options

    --cx-url CX_URL             The base URL for the CxOneFlow endpoint 
                                (e.g. https://cxoneflow.corp.com)


    Output Options

    --outfile CSVFILE          The path to a file where the audit CSV will be
                               written. [default: ./cxoneflow.csv]

    --no-config                Only include projects that are not configured
                               or are partially configured.

    Filtering Options

    --match-regex M_REGEX      Regular expression that matches ADO projects that
                               should be configured to send events to CxOneFlow.

    --skip-regex S_REGEX       Regular expression that matches ADO projects that
                               should not be configured to send events to CxOneFlow.

    SCM Options

    --pat PAT                  An SCM PAT with appropriate privileges.

    --pat-env                  Obtain the PAT from the environment variable 'CX_PAT'

    --scm-url URL              The URL to the SCM instance (e.g. https://dev.azure.com)
    """
    args = self._get_opts(self.ado_audit.__doc__, ["adoe", "audit"] + ado_args, help)

    return await AdoAuditor(args['--outfile'], args['--no-config'], targets=args['TARGETS'],
                            concurrency=self.concurrency, proxy=self.proxy,
                            ignore_ssl_errors=self.ssl_ignore,
                            match=self._matcher_factory(args['--skip-regex'], args['--match-regex']), 
                            pat=SCMTool.resolve_from_env(args['--pat'], "CX_PAT"), 
                            cx_url=args['--cx-url'], scm_url=args['--scm-url']).execute()

  async def ado_deploy(self, ado_args : List[str], help : bool = False):
    """Usage: cxoneflow-audit adoe deploy [--match-regex M_REGEX | --skip-regex S_REGEX]
                      (--shared-secret SECRET | --shared-secret-env) [--replace]
                      (--pat PAT | --pat-env) (--scm-url URL)
                      (--cx-url CX_URL) TARGETS...
    
    TARGETS...                  One or more collection names where service hook
                                configurations will be created on each project.

    Deployment Options

    --cx-url CX_URL             The base URL for the CxOneFlow endpoint 
                                (e.g. https://cxoneflow.corp.com)

    --shared-secret SECRET     The shared secret configured in the service hook

    --shared-secret-env        Obtain the shared secret from the environment variable 'CX_SECRET'

    --replace                  If an existing webhook subscription is found, replace it.

    Filtering Options

    --match-regex M_REGEX      Regular expression that matches ADO projects that
                               should be configured to send events to CxOneFlow.

    --skip-regex S_REGEX       Regular expression that matches ADO projects that
                               should not be configured to send events to CxOneFlow.

    SCM Options

    --pat PAT                  An SCM PAT with appropriate privileges.

    --pat-env                  Obtain the PAT from the environment variable 'CX_PAT'

    --scm-url URL              The URL to the SCM instance (e.g. https://dev.azure.com)

    """
    args = self._get_opts(self.ado_deploy.__doc__, ["adoe", "deploy"] + ado_args, help)
    
    return await AdoDeployer(SCMTool.resolve_from_env(args['--shared-secret'], 'CX_SECRET'), args['--replace'], 
                             targets=args['TARGETS'], concurrency=self.concurrency, proxy=self.proxy,
                            ignore_ssl_errors=self.ssl_ignore,
                            match=self._matcher_factory(args['--skip-regex'], args['--match-regex']), 
                            pat=SCMTool.resolve_from_env(args['--pat'], "CX_PAT"), 
                            cx_url=args['--cx-url'], scm_url=args['--scm-url']).execute()
  

  async def ado_remove(self, ado_args : List[str], help : bool = False):
    """Usage: cxoneflow-audit adoe remove [--match-regex M_REGEX | --skip-regex S_REGEX]
                      (--pat PAT | --pat-env) (--scm-url URL)
                      (--cx-url CX_URL) TARGETS...
    
    TARGETS...                  One or more collection names where service hook
                                configurations will be removed from each project.

    Deployment Options

    --cx-url CX_URL             The base URL for the CxOneFlow endpoint 
                                (e.g. https://cxoneflow.corp.com)

    Filtering Options

    --match-regex M_REGEX      Regular expression that matches ADO projects that
                               should be configured to send events to CxOneFlow.

    --skip-regex S_REGEX       Regular expression that matches ADO projects that
                               should not be configured to send events to CxOneFlow.
    SCM Options

    --pat PAT                  An SCM PAT with appropriate privileges.

    --pat-env                  Obtain the PAT from the environment variable 'CX_PAT'

    --scm-url URL              The URL to the SCM instance (e.g. https://dev.azure.com)
    """
    args = self._get_opts(self.ado_remove.__doc__, ["adoe", "remove"] + ado_args, help)
    
    return await AdoRemover(targets=args['TARGETS'], concurrency=self.concurrency, proxy=self.proxy,
                            ignore_ssl_errors=self.ssl_ignore,
                            match=self._matcher_factory(args['--skip-regex'], args['--match-regex']), 
                            pat=SCMTool.resolve_from_env(args['--pat'], "CX_PAT"), 
                            cx_url=args['--cx-url'], scm_url=args['--scm-url']).execute()
  

  async def ado_kickoff(self, ado_args : List[str], help : bool = False):
    """Usage: cxoneflow-audit adoe kickoff [--match-regex M_REGEX | --skip-regex S_REGEX]
                      (--pat PAT | --pat-env) (--scm-url URL) [--audit-file AUDIT_FILE]
                      (--ssh-key-path SSHKEY) [--ssh-key-pass SSHPASS | --ssh-key-env]
                      (--cx-url CX_URL) TARGETS...
    
    TARGETS...                  One or more collection names containing projects
                                for which all repositories will be scanned.

    Deployment Options

    --cx-url CX_URL             The base URL for the CxOneFlow endpoint 
                                (e.g. https://cxoneflow.corp.com)

    --audit-file AUDIT_FILE     A path to a file where audit data about the
                                started scans is written. Data is appended
                                to the file if it exists. [Default: kickoff_audit.csv]

    --ssh-key-path SSHKEY       The path to a file containing a PEM encoded
                                SSH private key for authenticating with the
                                CxOneFlow kickoff API

    --ssh-key-pass SSHPASS      The password to the SSH private key if it is
                                password protected.

    --ssh-key-env               Indicates that the SSH key password should be
                                obtained from the environment variable CX_SSHPASS.

    Filtering Options

    --match-regex M_REGEX      Regular expression that matches ADO projects that
                               should be configured to send events to CxOneFlow.

    --skip-regex S_REGEX       Regular expression that matches ADO projects that
                               should not be configured to send events to CxOneFlow.

    SCM Options

    --pat PAT                  An SCM PAT with appropriate privileges.

    --pat-env                  Obtain the PAT from the environment variable 'CX_PAT'

    --scm-url URL              The URL to the SCM instance (e.g. https://dev.azure.com)

    """
    args = self._get_opts(self.ado_kickoff.__doc__, ["adoe", "kickoff"] + ado_args, help)

    return await AdoKicker(targets=args['TARGETS'], concurrency=self.concurrency, proxy=self.proxy,
                            ignore_ssl_errors=self.ssl_ignore, audit_file_path=args['--audit-file'],
                            match=self._matcher_factory(args['--skip-regex'], args['--match-regex']), 
                            pat=SCMTool.resolve_from_env(args['--pat'], "CX_PAT"),
                            ssh_private_key_path=args['--ssh-key-path'], 
                            ssh_private_key_password=SCMTool.resolve_from_env(args['--ssh-key-pass'], "CX_SSHPASS"),
                            cx_url=args['--cx-url'], scm_url=args['--scm-url']).execute()


  async def __call__(self, ado_args : List[str], help : bool = False):
    """Usage: cxoneflow-audit adoe <command> [<args>...]

    <command> can be one of:
    audit       Execute an audit for CxOneFlow webhook deployment.

    deploy      Deploy CxOneFlow webhooks on the projects in the specified collections.

    remove      Remove CxOneFlow webhooks on the projects in the specified collections.

    kickoff     Iterate through project repositories in the specified collection
                and perform an initial scan on the default branch.

    Use "cxoneflow-audit help adoe <command>" for further help.
    """
    tool = [] if help else ["adoe"]
    return await self._dispatch(self.__call__.__doc__, "<command>", "<args>", tool + ado_args, help)



