function _make_proxies(proxy, origin, names) {
  names.forEach(function(name) {
      proxy[name] = eval("(function " + name + "() { return origin[name].apply(origin, arguments); })");
  });
  return proxy;
}

function _make_properties(proxy, origin, names) {
  names.forEach(function(name) {
      Object.defineProperty(proxy, name, {
          configurable: false,
          enumerable: true,
          get: function() {
              return origin[name];
          },
          set: function(value) {
              origin[name] = value;
          }
      });
  });
  return proxy;
}