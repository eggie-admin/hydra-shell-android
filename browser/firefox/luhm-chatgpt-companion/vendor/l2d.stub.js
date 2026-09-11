globalThis.L2D = globalThis.L2D || {
  __luhm_stub: true,
  init() {
    return {
      async load() {
        throw new Error("LUHM_LIVE2D_RUNTIME_NOT_INSTALLED");
      },
      destroy() {},
      getMotions() { return {}; },
      playMotion() {},
      setParams() {},
      setExpression() {},
      getExpressions() { return []; }
    };
  }
};
