from dify_plugin import Plugin, DifyPluginEnv

plugin = Plugin(DifyPluginEnv(MAX_REQUEST_TIMEOUT=120))

if __name__ == '__main__':
    # import pydevd_pycharm
    # pydevd_pycharm.settrace('localhost', port=8888, stdoutToServer=True, stderrToServer=True)
    plugin.run()
